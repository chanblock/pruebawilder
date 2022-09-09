
import csv
from django.utils.html import strip_tags
from pymongo import MongoClient
from datetime import datetime
#GRAPH 
from bokeh.embed import components
from bokeh.layouts import layout
from bokeh.models import HoverTool,DateRangeSlider,BoxZoomTool,WheelZoomTool,ResetTool,PanTool,ColumnDataSource
from bokeh.plotting import figure
from chanblockweb.settings.base import env
from bokeh.palettes import Category10


client = MongoClient(env('MONGOATLAS_USER'))
db = client.chancblock


def home():
    
    mtgoxdb=db.mtgox
    list_address_mtgox =list (mtgoxdb.find({},{"_id":0}))
    
    for valuemtgox in list_address_mtgox:
        valuemtgox['Remaining_BTC_amount']=valuemtgox['Remaining_BTC_amount']*0.00000001
        #print(valuemtgox['Remaining_BTC_amount']*0.00000001)
    getvalues= list(client.chancblock.mtgoxblance.find())
    dateX=[]
    valueY=[]
    for values in getvalues:
        auxdate=datetime.strptime(values['t'], '%d/%m/%Y')
        dateX.append(auxdate)
        value= float(values['v'])/1000
        valueY.append(value)

    # GRAFICA DATE
    plot = figure(x_axis_type="datetime", 
    sizing_mode="stretch_width",
    x_range=(dateX[0],dateX[-1]),
    tools=[HoverTool(
    formatters={
        '@x': 'datetime', # use 'datetime' formatter for '@date' field
    }
    ),
    BoxZoomTool(),
    WheelZoomTool(dimensions = 'height'),
    WheelZoomTool(dimensions = 'width'),
    ResetTool(),
    PanTool(),
    ],
    tooltips="Date: @x{%F}, Price USD: @y K",
    toolbar_location="above"
    )
    plot.xaxis.axis_label = 'Date'
    plot.yaxis.axis_label = 'BTC (UND) (k)'
    plot.xgrid.visible = False   
    plot.toolbar.active_drag = None
    plot.toolbar.logo = None
    plot.background_fill_color="#f7f8fa"
   
    plot.line(dateX, valueY)
    # # set up RangeSlider
    range_slider = DateRangeSlider(
        title="Date range",
        start=dateX[0],
        end=dateX[-1],
        step=1,
        value=(plot.x_range.start, plot.x_range.end),
    )
    range_slider.js_link("value", plot.x_range, "start", attr_selector=0)
    range_slider.js_link("value", plot.x_range, "end", attr_selector=1)
    # # create layout
    layout1 = layout(
        [
            [plot],
             [range_slider],
        ],
        sizing_mode='stretch_width',
        max_width=1450,
       
    )
    script, div = components(layout1)
    sum_totalBTC= list(mtgoxdb.aggregate([{"$group": {"_id":"null", "sum_val":{"$sum":"$Remaining_BTC_amount"}}}]))[0]['sum_val']*0.00000001
    var_totalBTC= list(mtgoxdb.aggregate([{"$group": {"_id":"null", "var_val":{"$sum":"$BTC_variation"}}}]))[0]['var_val']*0.00000001
    print((var_totalBTC))
    context= {
       'script': script,
       'div':div,
       'list_address_mtgox':list_address_mtgox,
       'total_BTC': sum_totalBTC


    }
    
    return context
    

def getAssets():   
    #connection to collection assets
    assetsdb = db.assets
    timestamp = str(datetime.now().date())
    # find by date
    list_assets =list (assetsdb.find({'date':timestamp},{"_id":0}))    
    if len(list_assets)==0:
        # find by last record
        last_record = assetsdb.find({},{"_id":0,"date":1}).sort("_id",-1).limit(1)
        last_record=list(last_record)[0]['date']
        list_assets = list(assetsdb.find({'date':last_record},{"_id":0}))
    for assets in list_assets:
        assets['metrics']['marketcap']['current_marketcap_usd']=assets['metrics']['marketcap']['current_marketcap_usd']/pow(10,6)

               #print(deltaChange(s[x]['symbol']),'getassets')
    #             s[x]['change7']=deltaChange(s[x]['symbol'])
                
    #             if s[x]['metrics']['market_data']['percent_change_usd_last_24_hours'] :
    #                 if deltaChange(s[x]['symbol']):
    #             #     s[x]['metrics']['market_data']['percent_change_usd_last_24_hours']=0
                
    #                  s[x]['change7']=s[x]['metrics']['market_data']['percent_change_usd_last_24_hours']-deltaChange(s[x]['symbol'])
    #             #
    #             #print(type(s[x]['change7']),'sssssss', type(s[x]['metrics']['market_data']['percent_change_usd_last_24_hours']))
                
    return list_assets

def deltaChange(symbol1):
    valor=0
    timestamp = datetime.now().date()
    #find by date
    d = datetime(timestamp.year, timestamp.month, (timestamp.day-7))

    assets_by_date = db.assets.find({"timestamp": {"$eq": d}},{"_id":0,"timestamp":0})
    for asset in assets_by_date:
        for coin in asset:
            if asset[coin]['symbol']== symbol1:
             valor= asset[coin]['metrics']['market_data']['percent_change_usd_last_24_hours']
   
                        
    return valor       

def coin_detail(symbol):
    #connection to collection assets
    assetsdb = db.assets
    detail=list( assetsdb.find({"symbol":symbol}).limit(1))   
    print(symbol)
    listMetric = detail[0]
    profile = db.profile.find({},{"_id":0,"timestamp":0}).sort("_id",-1).limit(1)                    
    roi_detail1=[]
    for key , value in zip(listMetric['metrics']['roi_by_year'].keys(),listMetric['metrics']['roi_by_year'].values()):       
        
        if value != 0:
            roi_detail1.append([key[:4] , value])
    listMetric['metrics']['roi_by_year']=roi_detail1

    #generacion de un list()para el tratamiento de los datos del profile
    profile_detail=list()
    for doc in profile:  
     for ind in doc:
        if doc[ind]['name']==listMetric['name']:
         profile_detail={'category':doc[ind]['profile']['general']['overview']['category']}
         profile_detail['tagline']=doc[ind]['profile']['general']['overview']['tagline']
         profile_detail['sector']=doc[ind]['profile']['general']['overview']['sector']         
         profile_detail['roadmap']=format_date(doc[ind]['profile']['general']['roadmap'])
         profile_detail['economics']=doc[ind]['profile']['economics']
        #eliminacion de tag con strip_tags 
         profile_detail['project_details']=strip_tags(doc[ind]['profile']['general']['overview']['project_details'])        
         profile_detail['technology']=strip_tags(doc[ind]['profile']['technology']['overview']['technology_details'])
         profile_detail['regulatory_details']=strip_tags(doc[ind]['profile']['general']['regulation']['regulatory_details'])
         profile_detail['governance']=strip_tags(doc[ind]['profile']['governance']['governance_details'])
         profile_detail['economics_launchDetails']=strip_tags(doc[ind]['profile']['economics']['launch']['general']['launch_details'])


    #find symbol_tradingview para el requeste del widget 
    symbol_coins = db.tickers.find({},{"_id":0,"symbol":0}).sort("_id",-1).limit(1) 
    for symbol_coin in symbol_coins:
        for aux in symbol_coin:
         if aux == symbol:   
         # print(aux,':',symbol_coin[aux])
          profile_detail['symbol_tradingview']=symbol_coin[aux]
    
    coin_detail={'asset': listMetric,'profile': profile_detail}  
   
    return coin_detail
def format_date(roadmap):
    for iterator in roadmap:
        aux = iterator['date'] 
        if iterator['date']:              
         dto = datetime.strptime(aux, "%Y-%m-%dT%H:%M:%SZ").date()                                         
         iterator['date']= dto
    
    return roadmap


def list_variable():
    list_variable=[]
    dir_file="static/VARIABLESCOINMETRICS.csv"
    dir_file1="static/metrics_name.csv"
    
    # with open(dir_file1) as File:
    #     reader = csv.reader(File, delimiter=',', quotechar=',',
    #                     quoting=csv.QUOTE_MINIMAL)  
    #     for variable in reader:
    #         print(variable[0].split(';'))            
            
    with open(dir_file1) as File:
        reader = csv.reader(File, delimiter=',', quotechar=',',
                        quoting=csv.QUOTE_MINIMAL)
        for variable in reader:            
            list_variable.append(variable[0].split(';'))

    return list_variable   

def  graph(symbol):
    print('assetUtil grafica symbol: ',symbol)
   
    value='AdrActCnt'
    listXY=[]
    unmetric=[]
    modelSymbol=[]
    
    # condicional para saber si la variable symbol es un array o str
    if type(symbol) == str:
        isArray=False
        print('dentro de if veiw.grafica')
        getvalues= list(client.coinmetrics[symbol].find({"PriceUSD":{"$exists":True}},{"_id":0, "time":1,"PriceUSD":1}))        
        listXY.append(getvalues)
        modelSymbol.append(symbol)
        print(len(listXY))
    if type(symbol) != str:
        isArray = True
        print('dentro de symbol no str',len(symbol['assets']))
        if len(symbol['metric']) == 1:            
            for i in symbol['assets']:
                getvalues= list(client.coinmetrics[i].find({symbol['metric'][0]:{"$exists":True}},{"_id":0, "time":1,symbol['metric'][0]:1}))
                if len(getvalues)==0:
                    unmetric.append(i)
                else:    
                    listXY.append(getvalues)
                    modelSymbol.append(i)
        if len(symbol['metric']) > 1:  
                for i in symbol['metric']:
                    getvalues= list(client.coinmetrics[symbol['assets'][0]].find({i:{"$exists":True}},{"_id":0, "time":1,i:1}))
                    if len(getvalues)==0:
                        unmetric.append(i)
                    else:  
                        listXY.append(getvalues)
                        modelSymbol.append(i)    
    dataX=[]
    dataY=[]

 

    if len(listXY) != 0:
        for getvaluesX in listXY:
            auxX=[]
            auxY=[]
            for value in getvaluesX:
                auxdate= datetime.fromisoformat(value['time'])
                auxX.append(auxdate)
                metric= list(value.keys())[1]
                if isArray:
                    if len(symbol['metric']) == 1:
                        value1=value[symbol['metric'][0]] 
                    else: 
                        value1=value[metric]         
                else:
                    value1= float(value['PriceUSD'])
                auxY.append(value1)
            print('******************')
            dataX.append(auxX)
            dataY.append(auxY)

        if isArray:
            if len(symbol['metric']) == 1:
                titleGraph = symbol['metric'][0]
            else: 
                titleGraph = symbol['assets'][0] 
            
        else:
            titleGraph='PriceUSD'
        
        df= {'X_value':dataX,
            'Y_value':dataY,
            'model': modelSymbol,
            'color': (Category10[3])[0:len(listXY)],

        }
        source=ColumnDataSource(df)

        listDate=[]
        for date in dataX:
            listDate.append(min(date))
            listDate.append(max(date))
        
  
        date_start=min(listDate)
        date_end=max(listDate)        
        pl = figure(x_axis_type="datetime", 
        title= titleGraph,
        sizing_mode="stretch_width",
        x_range=(date_start,date_end),
        tools=
        [BoxZoomTool(),
        WheelZoomTool(dimensions = 'height'),
        WheelZoomTool(dimensions = 'width'),
        ResetTool(),
        PanTool()],
        toolbar_location="above"
        )
        pl.toolbar.active_drag = None
        pl.toolbar.logo = None
        pl.multi_line(xs='X_value', ys='Y_value', legend="model",
                line_width=0.5, line_color='color',
                source=source)
        pl.add_tools(HoverTool(tooltips=
        [
            ('Date',  '$data_x{%F}'),
            ('Value', '$data_y'),
        ],
        formatters={
            '$data_x': 'datetime',
        },
        
        ))
        pl.xaxis.axis_label = 'Date'
        pl.yaxis.axis_label = titleGraph
        pl.xgrid.visible = False
        pl.background_fill_color="#f7f8fa"
        # # set up RangeSlider
        range_slider = DateRangeSlider(
            title="Date range",
            start=pl.x_range.start,
            end=pl.x_range.end,
            step=1,
            value=(pl.x_range.start, pl.x_range.end),
        )
        range_slider.js_link("value", pl.x_range, "start", attr_selector=0)
        range_slider.js_link("value", pl.x_range, "end", attr_selector=1)

        layout1 = layout(
            [            
                [pl],
                [range_slider],
                
            ],
            sizing_mode='stretch_width',
            max_width=1450,
        
        )
        script, div = components(layout1)

    
        #LIST CRYPTO COINMETRIC
        variable_coinmetrics= list_variable()
        showCollection= client.coinmetrics.list_collection_names()
        context= {
        'script': script,
        'div':div,
        'showcollection': showCollection,
        'variable_coinmetrics':variable_coinmetrics,
        'message': unmetric,
        'exist_plot':True
       

        }              
    else:


        context = {
            'exist_plot':False,
            'message': unmetric,
        } 
    print(unmetric)
    return context    

