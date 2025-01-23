

### Initial thoughts

so it seems that we are going to need some data services. yay!
I am going to be packaging the main tooling as a lib and try to import and use it in the notebook.
also I wish I could add the static checks to this env and repo setup, but maybe later.

so going back to the price service, we have some rest api to hit it seems.
we are going to establish an service interface, and API impelementation, and a service wrapper.
and some data types as contract.

so I figured the python api for the gridstatus and wrote  a simple client to get the price per node.

now on to the service.

### price service

so in the API we just passed the inputs, and added some checks and bounds on them,
but for the oututs no change pretty much on what we get from the endpoint.
we preferred to get a simple dict, but we get dataframe.

in the price service we want to place a few checks and bounds on outputs, we do a few things
    make the outputs data fit our defined contract
    post-processing for missing vals, checking coorect number of records, etc
    post-processing for changing resampling

okay so half-way into the price service development noticed that data set patterns 
and output tables for lmp, spp, and as prices are totally different,
so had to come back to make it more specific to get the energy prices for now.
the good news was that I could integrate between the spp and lmp for dam and rtm prices.

the other issue was that from the start my plan was (and still is) to avoid Dataframes and
convert them to objects and dataclasses, but for data analytics and corrolation analysis etc
that I intend to do, much would be done either with pandas or numpy

### analysis tools
okay so now we have some sort of price service that gives us the price for a product and
a node, etc. 
now on to making some analysis tools, for corrolation, cross-corrolation, variance etc.
now what, what kind of inference we want to get from the price data,
what kinds of relations to find? 
between DAM and RTM spp or DAM spp in different nodes,
 or RTM spp in different nodes 
 we want 
- see and compare volatility in which nodes of the RTM SPPs
- see if a patern exist in DART, daily, weekly, etc, in a given node
- see and compare the DART paterns is different nodes?
- see if a seasonal correlation exist between DAM and RTM high price days.
- see if a price voatility exist in a specific hours of the day/month/year