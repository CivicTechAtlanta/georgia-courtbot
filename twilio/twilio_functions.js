const { BigQuery } = require("@google-cloud/bigquery");
const fetch = require('node-fetch');
exports.handler = async function (context, event, callback) {
  console.log(`Query_bigquery function running. Event:`);
  console.log(event);

  // instantiate bigqueryClient as connection to GCP BigQuery
  let bigqueryClient;
  try {
    // The Google Cloud service account credentials are stored as a
    // Twilio asset. Get the path, then set the environment variable
    // so the Google/BigQuery library can find it.
    const path = Runtime.getAssets()["/gcp_service_account.json"].path;
    console.log("The service account path is: " + path);
    process.env.GOOGLE_APPLICATION_CREDENTIALS = path;
    bigqueryClient = new BigQuery();
  } catch (error) {
    console.log(error);
    return callback(error);
  }

  if (event.user_text) {
    try {
      // input is user_text
      // run query to verify if this is a valid case number that exists in the db

      str = event.user_text.trim().toUpperCase();

      // returns the first non-null match
      regex_res =
        str.match(/(\d{2})([A-Z]{1,2})(\d{4,5})/) ||
        str.match(/([A-Z]{1})(\d{7})/);
      let caseNumber = regex_res[0]
      // const sqlQuery = `
      //   SELECT *
      //   FROM \`cfa-georgia-courtbot.STG.HEARING\`
      //   WHERE CaseNumber='${caseNumber}'
      //   LIMIT 1`;
      // console.log(sqlQuery);

      // const options = {
      //   query: sqlQuery,
      //   // Location must match that of the dataset(s) referenced in the query.
      //   location: "us",
      // };

      // const [rows] = await bigqueryClient.query(options);
      // console.log("BigQuery result:");
      // console.log(rows);
      

      // if (rows.length) {
        console.log(caseNumber);
      var result = await fetch(`https://us-east1-cfa-georgia-courtbot.cloudfunctions.net/getHearing?caseNumber=${caseNumber}`);
      if( result.ok ) {
        // If we have a result, get it as json
        var json = await result.json();
        if( // Check that we got back the kind of data we wanted, and it contains at least one hearing result
              json.hasOwnProperty('Data') 
              && json.Data.length > 0 
              && json.Data[0].hasOwnProperty('CaseNumber')
        ) {
          var hearing = json.Data[0];
          const dataset = bigqueryClient.dataset('STG');
          const table = dataset.table('SUBSCRIPTION');
          let data = await table.insert({
            CaseNumber: caseNumber,
            PhoneNumber: event.user_phone
          })

          return callback(null, {
            hearing_found: true,
            // date: rows[0].HearingDate.value,
            // time: rows[0].HearingTime,
            // courtroom: rows[0].CourtRoom,
            date: hearing.HearingDate,
            time: hearing.HearingTime,
            courtroom: hearing.CourtRoom
          });
        }
        else
        {
          return callback({ hearing_found: false });
        }
      } else {
        return callback({ hearing_found: false });
      }
    } catch (error) {
      console.log(error);
      return callback(error);
    }
  }
};