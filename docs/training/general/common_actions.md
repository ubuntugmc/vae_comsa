# Common Actions Across User Roles

## Signing in for the First Time

Signing into VA Explorer requires an email address and password. You will use a
temporary password obtained from either system-generated email or your
administrator when signing in for the first time. Contact your admin if you do
not have a temporary password or cannot find it.

1. Navigate to VA Explorer in your web browser. Compatible web browsers include
Google Chrome, Microsoft Edge, Mozilla Firefox, and Apple Safari.

1. Use your email address and your temporary password to sign in. You will be
prompted to choose a new password on the next page. Follow the instructions to
create a strong password that will help protect your VA Explorer account.

1. After signing in, the application will take you to the Home page. The Homepage
shows trends of VAs collected and coded, as well as a snapshot of VAs with
coding issues and VAs coded with Indeterminate cause of death. The scope of VA
data shown on the Home page depends on your assigned role and geographic access.

- **For Field Workers:** If you are assigned the Field Worker role, the Homepage
  shows trends and data on the VAs that you have conducted.
- **For All Other Roles:** For all other roles, data on the Home page are
  limited to the specific regions or facilities you can access.

## Viewing Your Account Profile

Your profile shows the role you have been assigned, your geographic access, and
actions you can take in VA Explorer, such as viewing PII and downloading data.
These account settings are described in User Roles and Capabilities (link) To
view your account profile:

1. Click your name in the upper righthand corner of the navigation bar; a
dropdown menu will open.

1. Click the “My Profile” option within the dropdown menu.

Please contact your administrator if you need to update your account settings or
if something looks incorrect. Only individuals with administrator roles can
update user accounts.

## Changing Your Password

To change your password while signed into VA Explorer:

1. Click your name in the upper righthand corner of the navigation bar; a
dropdown menu will open.

1. Click the “Change Password” option within the dropdown menu.

1. Enter your current password.

1. Choose a new password, following instructions to enter a valid password twice.

If you do not know your current password, sign out of VA Explorer and click
“Forgot Password?” You will be instructed to enter the e-mail address associated
with your account, and VA Explorer will send an email with a link allowing you
to reset it.

## Using the Analytics Dashboard

All users can view the VA Analytics Dashboard to see information on the VAs
(filtered to their level of permissions and access) that have successfully been
assigned a cause of death. To do so, click “Dashboard” in the navigation bar to
view it.

The VA Analytics Dashboard is a dynamic, visualization-based dashboard that helps
you explore cause of death data. It has three global filters that simultaneously
update all graphs, maps, and statistics found in the top left of the dashboard
page and directly above the heatmap. The global filters include:

```{csv-table}
:header-rows: 1
:stub-columns: 2
:escape: \
Filter,Description,How To Use
Death Date,View analytics for a specific date of death timeframe,Choose the timeframe you want to explore from the Time Period dropdown menu (ex. Within 1 Month\, Within 1 Year\, or Custom)
Cause of Death,View analytics for a particular cause of death,Choose a cause of death or a category of causes (ex. Infectious\, NCD\, etc.) from the Causes dropdown menu
Location,Filter analytics to specific location(s),Choose specific geographic regions using the province/district selector and location dropdown or click a region on the map.
```

## Viewing Dashboard Components

The Dashboard includes several visualizations, including:

- A dynamic heatmap showing geographical trends, with ability to filter for
regions of interest. Found in the bottom left of the dashboard page.

- Cause of death plots. Found in the top right of the dashboard page.

- Death distributions by age, gender, and place of death (“demographics”).
Found in the bottom right of the dashboard page.

- Cause of death trends over time. Found in the middle right of the dashboard page.

## Searching for and Reviewing Specific VAs

All roles have some level of access to search for and review specific VAs. To do
so, click “Data Management” in the navigation bar to view the Data Management
page.

The Data Management page shows a paginated table of all the VAs in the system
your account is eligible to see. For more information about your account and
eligibility, see Viewing Your Account Profile (link). On the Data Management
page, you can search or filter available VAs with the following parameters:

```{csv-table}
:header-rows: 1
:stub-columns: 1
:escape: \
Field,Description
ID,The unique numeric identifier assigned to the specific VA in VA Explorer. 
Submitted,The date the VA was submitted. If your account does not have PII access\, you will see “Date Unknown.”
Facility,The facility where the VA was collected. If facility information is missing\, you will see “Location Unknown.”
Deceased,The name of the deceased individual. If your account does not have PII access\, you will see “Subject Unknown.”
Deathdate,The date of the individual’s death. If your account does not have PII access\, you will see “Date Unknown.”
Cause,The cause of death assigned by coding algorithm. If the VA has not yet been coded\, “Not Coded” will be displayed. A VA is “Not Coded” if the algorithm has not been run or if error(s) prevent the VA from being coded. 
Warnings,The count of warnings generated by the coding process. An example of a warning you might see for InterVA5 is: “field ageInYears\, age was not provided or not a number.”
Errors,The count of errors generated by the coding process. An example of an error you may see for InterVA5 is: “Error in age indicator: Not Specified.”
```

In addition to searching and filtering, users may also have access to the
following actions depending on their permissions:

- Sort VA table data by column value by clicking any of the column headers.
Clicking again reverses the sort order of the column

- Download VA table data by clicking the “Export” button to be directed to the
Export page with your search parameters automatically filled into the export form.

- View VA details by clicking the “View” button on any individual VA. See
details below.

## Viewing Details for Individual VAs

When viewing a specific VA, the resulting page may show a couple of tabs at the
top below the VAs ID. Users with permission to change VAs will also see the
option to repair the VA via an “Edit Record” button. See Repairing VA Errors &
Warnings (link) for details on editing VAs. Quick navigation options to
automatically scroll to the top or bottom of the VA responses is available via
the floating action button in the bottom right.

### Record

This tab is always visible and shows the VA questionnaire data, including:

- The question ID corresponding to the WHO standard instrument
- The text of question associate that pairs with each question ID
- The response or calculation for each question

By default, all empty fields are hidden so that only questions with answers are
shown. Revealing these is possible by unchecking the “Hide Empty Fields” box in
the top right of this tab.

### Coding Issues

This tab will become visible if the individual VA has any warnings or errors
associated with it.

These warnings and errors can be applied during data import or, more often,
after processing the VA for cause of death.

- **(Errors)** these are issues that either VA Explorer or a coding algorithm
has determined is severe enough to totally prevent CoD assignment. They will
need to be corrected.

- **(User Warnings)** these are issues that should be addressed because they
potentially block CoD assignment or the accuracy of the assigned CoD but are
not quite as severe.

- **(Algorithm Warnings)** these are warnings specifically provided by the
algorithm after assigning a CoD that indicate the assignment may not be accurate.
Fixing these increases the accuracy of CoD assignment. This tab will be visible
if the individual VA has been edited or updated in any way since its initial import.

### Change History

This history provides for transparency, record integrity, and protection from
misuse for VAs and will take the form of an audit trail, a table of all changes,
with each row showing

- the date of the change
- the user who made the change
- The fields before and after the change

Additionally, this tab will contain two action buttons:

- **(Reset to Original)** to completely reset the VA to the state it was in at
the time of original import. (Note that for this action, change history is still
preserved)

- **(Revert Most Recent Change)** to erase or undo the change described at the
top of the change history table (organized by most recent changes first)

```{admonition} Duplicate VAs
If your system is configured to automatically flag potential duplicate VAs, you
may also see a yellow warning banner above these tabs. This banner alerts you
that VA Explorer has flagged this VA as a possible duplicate. Please consult
with an administrator or data manager to determine any actions to take for
potential duplicate VAs.
```