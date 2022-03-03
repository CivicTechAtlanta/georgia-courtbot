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

      // Standardized logging: https://cloud.google.com/functions/docs/monitoring/logging
      const globalLogFields = {};
      if (typeof req !== 'undefined') {
            const traceHeader = req.header('X-Cloud-Trace-Context');
            if (traceHeader && project) {
                  const [trace] = traceHeader.split('/');
                  globalLogFields['logging.googleapis.com/trace'] = `projects/${project}/traces/${trace}`;
            }
      }

      let bigquery = new BigQuery();
      const sqlQuery = `
            SELECT *
            FROM \`cfa-georgia-courtbot.STG.HEARING_NOTIFY_VIEW\`
            WHERE 1=1`;

      const [rows] = await bigquery.query({
            query: sqlQuery,
            location: "us",
      });

      if ( rows.length ) {
            let count = 0;
            for( var i=0; i<rows.length; i++ ) {
                  var row = rows[i];
                  var response = await twilio.messages.create({
                        from: '+19362593013',
                        to: row.PhoneNumber,
                        body: `Don't forget your hearing is coming up on ${row.HearingDate.value} ${row.HearingTime} at ${row.CourtRoom}!`
                  });
                  console.log(response);
                  if( response.error_log )
                  {
                        const entry = Object.assign(
                              {
                                    severity: 'ERROR',
                                    message: `Twilio: ${response.error_message}`,
                                    caseNumber: row.CaseNumber || 'No Case Number',
                              },
                              globalLogFields
                        );
                        console.log(JSON.stringify(entry));
                  }
                  else
                  {
                        count++;
                  }
            }
      }
      let message = JSON.stringify(rows);
      res.status(200).send(message);
};
