""" Ok, here's the plan.
We should implement a DataEngine with two sources.
The first source will always return a single list of IDs (QStringList wrapped in QVariant).
The second source can be queried by ID, and will return the actual loan details for the given ID.
(This might actually not be possible; in that case, what ?)

The we should implement a Service that will be used to write to the engine.
e.g.
 Plasma::DataEngine *twitter = dataEngine("twitter");
 Plasma::Service *service = twitter.serviceForSource("aseigo");
 service.setParent(self) # to autodelete once done, might not be required
 KConfigGroup op = service->operationDescription("update");
 op.writeEntry("tweet", "Hacking on plasma!");
 Plasma::ServiceJob *job = service->startOperationCall(op);
 connect(job, SIGNAL(finished(KJob*)), this, SLOT(jobCompeted()));

Problems:
* a lot of work!
* 
* we need to generate unique IDs every time we add a loan to the list
"""

