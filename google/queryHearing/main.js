var QueryHearing = require('./QueryHearing');
// process.env.TZ = "America/New_York"
var d = new Date();
var startDate = d.toLocaleDateString();
d.setDate(d.getDate() + 365*5);
var endDate = d.toLocaleDateString();

// var hearings = new QueryHearing({
//     startDate,
//     endDate,
//     userAgent: 'test'
// });
// hearings.startSesssion()
// .then( () => {
//     hearings.getCase('20FM3016')
//     .then((json) => {
//         console.log(json);
//     });
// })

async function init() {
    var hearings = new QueryHearing({
        startDate,
        endDate,
        // userAgent: 'test'
    });
    await hearings.startSesssion()
    var json = await hearings.getCase('21FM10721');
    console.log(json);
    var hearingDate = new Date(json.Data[0].HearingDate);
    console.log(hearingDate)
    var now = new Date();
    now.setHours(0);
    now.setMinutes(0);
    now.setSeconds(0);
    now.setMilliseconds(0);
    var currDate = now.getTime();
    var diff = hearingDate.getTime() - currDate;
    var secsPerDay = 1000*60*60*24
    var is1Day = ( diff == secsPerDay );
    var is3Day = ( diff == secsPerDay * 3);
    var isPast = ( diff == secsPerDay < 0);
    console.log( hearingDate.getTime(), currDate, now.toUTCString(), hearingDate.toUTCString(), diff, secsPerDay*3, is1Day, is3Day )
}
init();