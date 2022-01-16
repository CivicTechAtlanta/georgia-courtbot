# georgia-courtbot
Helping people remember to attend court to help break the cycle of fines and jail time

### Notes for Contributors
* [Issues in this Repo](https://github.com/codeforatlanta/georgia-courtbot/issues)
* [Quick Start Guide](https://docs.google.com/document/d/1folvVL2UYl3UeBU9jRcmf5AXU74px8gJmmkvKt6KJ7Q/edit?usp=sharing)
* [Code For Atlanta slack --> #georgia-courtbot channel](https://codeforatlanta.slack.com)

### Roadmap

* **Version 1 (MVP)**: Dekalb County scraper built & single copy of dataset captured.  Simple SMS functionality set up based off of that data
  - Tech Components:
    - Data scraper for Dekalb county
    - Data saved in place SMS tool can pick up
    - Simple SMS functionality
    - Notification system that triggers text to be sent
  - Design Needs:
    - Easy-to-manage online form (e.g. Google forms or AirTable)
    - Usability research

* **Version 2**: Dekalb County scraper running daily in the cloud, pushes data into database.  Website similar to https://court.bot facilitates sign up for court date reminders via SMS
  - Components (in addition to MVP1):
    - Database
    - Website
    - SMS sign-up
    - Reminder scheduler
  - Design Needs:
    - UX Flows

* **Version 3+ (Potential Features)**
  - Additional counties / municipalities
  - Integration with other courtbot implementation(s)
  - Additional messaging besides SMS
