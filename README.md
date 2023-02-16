# Cherry Blossom 10 Miler Forum Checker

I really want to run the Cherry Blossom 10 Miler, but I didn't get a spot in the
lottery. There is a bib transfer period where folks who cannot run the race anymore for
whatever reason can transfer their entries to individuals who do want to run the race.
This is all coordinated on a rather old-school but very active [message board](https://secure.marathonguide.com/Forums/CherryBlossomTenMile.cfm?step=1&Topic=175). Bib-seekers outnumber bib offers 10:1, and
posts offering a bib frequently get multiple responses in just a few minutes. The
message board doesn't have any sort of notification functionality, so I built my own!
This python script is deployed as a Google Cloud Function, and runs every few minutes
to let me know if there has been a new message board post worth responding to.
