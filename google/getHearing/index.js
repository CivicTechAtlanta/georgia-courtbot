
/**
 * Responds to any HTTP request.
 *
 * @param {!express:Request} req HTTP request context.
 * @param {!express:Response} res HTTP response context.
 */
 process.env.TZ = "America/New_York"
 exports.getHearing = async (req, res) => {
 var QueryHearing = require('./QueryHearing');
     var json = req.query;
     if( req.query.caseNumber ) {
         var d = new Date();
         d.setDate(d.getDate() -30 );
         var startDate = d.toLocaleDateString();
         d.setDate(d.getDate() + 395 );
         var endDate = d.toLocaleDateString();
 
         var hearings = new QueryHearing({
             startDate,
             endDate,
             // userAgent: 'test'
         });
         await hearings.startSesssion();
         json = await hearings.getCase( req.query.caseNumber );
     }
     res.status(200).json(json);
 };
 