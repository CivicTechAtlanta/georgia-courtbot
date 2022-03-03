const fetch = require('node-fetch');

process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";

module.exports = class QueryHearing {

    constructor( { startDate, endDate, userAgent } ) {

        this.startDate = startDate;
        this.endDate = endDate;
        this.cookies = null;
        this.userAgent = userAgent || 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.111 Safari/537.36'
    }

    parseCookies(rawCookies) {
        this.cookies = rawCookies.map((entry) => {
            const parts = entry.split(';');
            const cookiePart = parts[0];
            return cookiePart;
        }).join(';');
        console.log({ rawCookies, cookies: this.cookies } );
    }

    async getCase( caseNumber ) {

        var response = await fetch('https://ody.dekalbcountyga.gov/portal/Hearing/SearchHearings/HearingSearch', {
            credentials: 'include',
            headers: {
                'User-Agent': this.userAgent,
                'cookie': this.cookies
            },
            method: 'POST',
            redirect: 'follow',
            body: this.formData({
                "PortletName": "HearingSearch",
                "Settings.CaptchaEnabled": "False",
                "Settings.DefaultLocation": "All Courts",
                "SearchCriteria.SelectedCourt": "All Courts",
                "SearchCriteria.SelectedHearingType": "All Hearings",
                "SearchCriteria.SearchByType": "CaseNumber",
                "SearchCriteria.SearchValue": caseNumber,
                "SearchCriteria.DateFrom": this.startDate,
                "SearchCriteria.DateTo": this.endDate,
            })
        });


        var response = await fetch('https://ody.dekalbcountyga.gov/portal/Hearing/HearingResults/Read', {
            credentials: 'include',
            headers: {
                'User-Agent': this.userAgent,
                'cookie': this.cookies
            },
            method: 'POST',
            body: this.formData({
                'sort': '',
                'group': '',
                'filter': '',
                'portletId': '27'
            })
        });
        var json = await response.json();
        return json;
    }

    startSesssion() {
        return fetch('https://ody.dekalbcountyga.gov/portal/Home/Dashboard/26', {
            credentials: 'include',
            headers: {
                'User-Agent': this.userAgent
            }
        }).then((response) => {
            var headers = response.headers.raw();
            this.parseCookies(headers['set-cookie']);
        });  
    }

    formData(data) {
        const formData = new URLSearchParams();
        Object.entries(data).forEach((item) => {
            formData.set(item[0], item[1]);
        });
        return formData
    }
} 