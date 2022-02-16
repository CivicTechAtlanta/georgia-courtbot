const { BigQuery } = require("@google-cloud/bigquery");
const accountSid = process.env.TWILIO_ACCOUNT_SID;
const authToken = process.env.TWILIO_AUTH_TOKEN;
const twilio = require('twilio')(accountSid, authToken);
/**
 * Responds to any HTTP request.
 *
 * @param {!express:Request} req HTTP request context.
 * @param {!express:Response} res HTTP response context.
 */

exports.helloWorld = async (req, res) => {
  let bigquery = new BigQuery();
  const sqlQuery = `
        SELECT *
        FROM \`cfa-georgia-courtbot.STG.HEARING_NOTIFY_VIEW\`
        WHERE 1=1`;

  const [rows] = await bigquery.query({
        query: sqlQuery,
        location: "us",
  });

  console.log({rows});

  if (rows.length) {
      console.log(rows.length);
      for( var i=0; i<rows.length; i++ ) {
            var row = rows[i];
            console.log(row);
            var response = await twilio.messages.create({
                  from: '+19362593013',
                  to: row.PhoneNumber,
                  body: `Don't forget your hearing is coming up on ${row.HearingDate.value} ${row.HearingTime} at ${row.CourtRoom}!`
            });
            console.log(response);
      }
  }
  let message = JSON.stringify(rows);
  res.status(200).send(message);
};
