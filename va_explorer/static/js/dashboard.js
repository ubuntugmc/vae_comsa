Vue.use('stacked-bar-chart', 'line-chart', 'loader-spinning')

const dashboard = new Vue({
    el: '#dashboardApp',
    delimiters: ["<%", "%>"],
    data() {
        return {
            csrftoken: "",

            // map related values
            map: null,
            geojson: {},
            layer: null,

            //
            COD_grouping: [],
            COD_trend: null,
            place_of_death: null,
            demographics: null,
            geographic_province_sums: null,
            geographic_district_sums: null,
            uncoded_vas: 0,
            update_stats: {
                last_update: null,
                last_submission: null,
            },

            // chart sizes
            demographicsHeight: 0,
            demographicsWidth: 0,
            codHeight: 0,
            codWidth: 0,

            // dropdowns options and selected values
            listOfCausesDropdownOptions: [],
            locationTypesDropdownOptions: ["Province", "District"],
            deathDateDropdownOptions: ["Any Time", "Within 1 Month", "Within 3 months", "Within 1 year", "Custom"],
            deathDateSelected: "Any Time",
            startDate: "",
            endDate: "",
            causeSelected: "",
            borderType: "Province",
            colorScale: [
                "#4575b4", "#74add1", "#abd9e9", "#e0f3f8", "#ffffbf",
                "#fee090", "#fdae61", "#f46d43", "#d73027"
            ]
        }
    },
    computed: {
        highlightsSummaries() {
            return {
                "Coded VAs": d3.sum(this.COD_grouping.map(item => item.count)),
                "Uncoded VAs": this.uncoded_vas,
            }
        },
        geographicSums() {
            if (this.borderType === 'Province') {
                return this.geographic_province_sums
            } else if (this.borderType === 'District') {
                return this.geographic_district_sums
            }
        },
        locations() {
            // Used to generate options in "Geographic Distributions" select dropdown
            if (!this.geographic_province_sums || !this.geographic_district_sums) return []
            const provinces = this.geographic_province_sums.map(item => item.province_name)
            const districts = this.geographic_district_sums.map(item => item.district_name)
            return [...provinces, ...districts]
        },
        geoScale() {
            // A better way to do this would be to import d3 scale and use a quanitzed scale
            // but import is large
            if (!this.geographicSums) return
            const geoMax = Math.max(...this.geographicSums.map(item => +item.count)) + 100
            const geoMin = 0
            const n = 10
            const step = (geoMax - geoMin) / (n - 1)
            return Array.from({length: n}, (_, i) => geoMin + step * i)
        },
        dynamicCODHeight() {
            return this.COD_grouping.length === 1 ? (1 / 2) * this.codHeight : (4 / 5) * this.codHeight
        },
    },
    async created() {
        // Request data from API endpoint
        await this.getData()

        // assign list of causes for 'Cause of Death' dropdown
        this.listOfCausesDropdownOptions = this.COD_grouping.map(item => item.cause).sort()

        // Request geojson data
        const url = `${window.location.protocol}//${window.location.hostname}:${window.location.port}/static/`
        const geojsonRes = await fetch(`${url}/data/zambia_geojson.json`)
        this.geojson = await geojsonRes.json()
    },
    async mounted() {
        this.resizeCharts()
        window.addEventListener('resize', this.resizeCharts)

        await this.initializeBaseMap()
    },
    beforeDestroy() {
        // necessary to remove resize listener to avoid memory leak after switching to different view
        window.removeEventListener('resize', this.resizeCharts)
    },
    methods: {
        async getData() {
            /*
            fetch data for charts from API and assign all data variables for charts
             */

            const {startDate, endDate} = this.getStartAndEndDates()

            // TODO change hostname for production
            this.csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            const data_url = 'http://localhost:8000/va_analytics/api/dashboard?'
            const dataReq = await fetch(data_url + new URLSearchParams({
                start_date: startDate,
                end_date: endDate,
                cause_of_death: this.causeSelected,
            }), {
                method: 'GET',
                headers: {'X-CSRFToken': this.csrftoken, 'Content-Type': 'application/json'},
                mode: 'same-origin'
            })

            const jsonRes = await dataReq.json()
            this.COD_grouping = jsonRes.COD_grouping
            this.COD_trend = jsonRes.COD_trend
            this.place_of_death = jsonRes.place_of_death
            this.demographics = jsonRes.demographics
            this.geographic_province_sums = jsonRes.geographic_province_sums
            this.geographic_district_sums = jsonRes.geographic_district_sums
            this.uncoded_vas = jsonRes.uncoded_vas
            this.update_stats = jsonRes.update_stats
        },
        async initializeBaseMap() {
            /*
            use to set base map with tile on initial load
             */
            this.map = L.map('map').setView([-13, 27], 6)

            this.map.attributionControl.setPrefix('')

            const tiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 10,
                attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            }).addTo(this.map)
        },
        addGeoJSONToMap() {
            /*
            remove any existing choropleth layer and add new layer
             */
            const vm = this
            if (this.layer) this.map.removeLayer(this.layer)

            const borders = ['Country', this.borderType]
            let geojson = JSON.parse(JSON.stringify(this.geojson))
            geojson.features = this.geojson.features.filter(feature => {
                return borders.includes(feature.properties.area_level_label)
            })
            this.layer = L.geoJson(geojson, {
                style: function (feature) {
                    if (feature.properties.area_level_label !== 'Country') {
                        const color = vm.getColor(feature)
                        return {stroke: true, weight: 2, color, opacity: 1, fillColor: color, fillOpacity: 0.7}
                    } else {
                        return {weight: 2.5, opacity: 1, color: 'grey', stroke: true}
                    }
                }
            }).addTo(this.map)
                // .bindTooltip(function (layer) {
                //     console.log(layer)
                // }).addTo(this.map)
        },
        getMonth(date) {
            /*
            Extract year and month for line chart
             */
            const month = date.getUTCMonth()
            const year = date.getUTCFullYear()
            return new Date(year, month, 0)
        },
        getColor(feature) {
            const {area_name, area_level_label} = feature.properties
            const area = `${area_name} ${area_level_label}`
            const geo_sums = this.borderType === 'Province' ? this.geographic_province_sums : this.geographic_district_sums
            const geo_accessor = this.borderType === 'Province' ? 'province_name' : 'district_name'

            const results = geo_sums.find(item => item[geo_accessor] === area)
            if (results) {
                const count = results.count
                for (let i = 0; i < this.geoScale.length; i++) {
                    if (count > this.geoScale[i] && count < this.geoScale[i + 1]) {
                        return this.colorScale[i]
                    }
                }
            } else {
                return '#c0c0c0'
            }
        },
        getStartAndEndDates() {
            let date
            switch (this.deathDateSelected) {
                case "Any Time":
                    return {startDate: "", endDate: ""}
                case "Within 1 Month":
                    date = new Date()
                    date.setMonth(date.getMonth() - 1)
                    return {startDate: date.toISOString().slice(0,10), endDate: ""}
                case "Within 3 months":
                    date = new Date()
                    date.setMonth(date.getMonth() - 3)
                    return {startDate: date.toISOString().slice(0,10), endDate: ""}
                case "Within 1 year":
                    date = new Date()
                    date.setFullYear(date.getFullYear() - 1)
                    return {startDate: date.toISOString().slice(0,10), endDate: ""}
                case "Custom":
                    return {startDate: this.startDate, endDate: this.endDate}
            }
        },
        resizeCharts() {
            /*
            Apply method on mounted and with window event listener to automatically resize charts
             */
            this.demographicsWidth = this.$refs.demographics.clientWidth - 1
            this.demographicsHeight = this.$refs.demographics.clientHeight - 1

            this.codWidth = this.$refs.cod.clientWidth - 1
            this.codHeight = this.$refs.cod.clientHeight - 1
        },
        async updateDataAndMap() {
            await this.getData()
            this.addGeoJSONToMap()
        },
        async resetAllDataToActive() {
            // use this to reset all dashboard filters and retrieve the initial data
            this.startDate = ""
            this.endDate = ""
            this.causeSelected = ""
            this.deathDateSelected = "Any Time"
            await this.updateDataAndMap()
        },
    },
    watch: {
        // assign watchers to update map choropleth since it does not happen automatically
        geojson() {
            this.addGeoJSONToMap()
        },
        borderType() {
            this.addGeoJSONToMap()
        },
    }
})