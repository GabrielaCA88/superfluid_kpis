import pandas as pd
import requests
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
import datetime
import dateutil.relativedelta
from bs4 import BeautifulSoup
import math
import random

import dash
from dash import html
import dash_bootstrap_components as dbc

app = dash.Dash(__name__)

# ------------------------------------------------------------
# URL
url = 'https://api.thegraph.com/subgraphs/name/superfluid-finance/protocol-v1-matic'
transport = AIOHTTPTransport(url=url)
client = Client(transport=transport)

# Events query
query_event = gql("""
query AgreementLiquidatedEvents {
  agreementLiquidatedByEvents
    (where: { timestamp_lt: 1643276857, timestamp_gt: 1642067237})
   {
    blockNumber
    bondAccount
    id
    liquidatorAccount
    penaltyAccount
    rewardAmount
    bailoutAmount
    token
    timestamp
  }
}
""")
# Pre event snapshot
response_event = client.execute(query_event)
block_numbers = []
event_timestamps = []
penaltyAccounts = []
tokens = []
for x in range(0, len(response_event['agreementLiquidatedByEvents'])):
    block_numbers.append(int(response_event['agreementLiquidatedByEvents'][x]['blockNumber']))
    event_timestamps.append(int(response_event['agreementLiquidatedByEvents'][x]['timestamp']))
    penaltyAccounts.append(response_event['agreementLiquidatedByEvents'][x]['penaltyAccount'])
    tokens.append(response_event['agreementLiquidatedByEvents'][x]['token'])

ids = list(map('-'.join, zip(penaltyAccounts, tokens)))

# pre event snapshot
balanceUntilUpdatedAts = []
totalNetFlowRates = []
updatedAtTimestamps = []
token_names = []
for number, num in zip(block_numbers, ids):
    # Retrieving AccountTokenSnapshot:
    q_block = str(number - 1)
    query_token = gql(f"""
    query AccountTokenSnapshot {{
      accountTokenSnapshot(
        id:"{str(num)}"
        block: {{number:{q_block}}}
      ) {{token {{
      symbol}}
        balanceUntilUpdatedAt
        updatedAtTimestamp
        totalNetFlowRate
      }}
    }}
    """)

    response_token = client.execute(query_token)
    balanceUntilUpdatedAts.append(int(response_token['accountTokenSnapshot']['balanceUntilUpdatedAt']))
    totalNetFlowRates.append(int(response_token['accountTokenSnapshot']['totalNetFlowRate']))
    updatedAtTimestamps.append(int(response_token['accountTokenSnapshot']['updatedAtTimestamp']))
    token_names.append(response_token['accountTokenSnapshot']['token']['symbol'])
#
# Time relation
rds = []
rd_days = []
rd_hours = []
rd_minutes = []
rd_seconds = []
for event_timestamp, updatedAtTimestamp in zip(event_timestamps, updatedAtTimestamps):
    dt1 = datetime.datetime.fromtimestamp(updatedAtTimestamp)
    dt2 = datetime.datetime.fromtimestamp(event_timestamp)
    rd = dateutil.relativedelta.relativedelta(dt2, dt1)
    # rds.append (rd)
    rd_days.append(rd.days)
    rd_hours.append(rd.hours)
    rd_minutes.append(rd.minutes)
    rd_seconds.append(rd.seconds)

df_delta = pd.DataFrame(
    {'days': rd_days,
     'hours': rd_hours,
     'minutes': rd_minutes,
     'seconds': rd_seconds,
     'token': token_names
     })
df_delta['days_tomin'] = df_delta['days'] * 1440
df_delta['hours_tomin'] = df_delta['hours'] * 60
df_delta['sec_tomin'] = df_delta['seconds'] * 0.0166667
df_delta['delta'] = df_delta['days_tomin'] + df_delta['hours_tomin'] + df_delta['sec_tomin'] + df_delta['minutes']
df_delta['delta'].median()  # minutes
now = df_delta['delta'].median()


def transform_minutes(total_minutes):
    days = math.floor(total_minutes / (24 * 60))
    leftover_minutes = total_minutes % (24 * 60)

    hours = math.floor(leftover_minutes / 60)
    mins = total_minutes - (days * 1440) - (hours * 60)
    new_min = int(float(mins))
    # out format = "days-hours:minutes:seconds"
    out = '{} days, {} hours {} minutes'.format(days, hours, new_min)
    return out



# Relation with previous two weeks
query_event = gql("""
query AgreementLiquidatedEvents {
  agreementLiquidatedByEvents
    (where: { timestamp_lt: 1642067237, timestamp_gt: 1640991600})
   {
    blockNumber
    bondAccount
    id
    liquidatorAccount
    penaltyAccount
    rewardAmount
    bailoutAmount
    token
    timestamp
  }
}
""")

response_event = client.execute(query_event)
block_numbers = []
event_timestamps = []
penaltyAccounts = []
tokens = []
for x in range(0, len(response_event['agreementLiquidatedByEvents'])):
    block_numbers.append(int(response_event['agreementLiquidatedByEvents'][x]['blockNumber']))
    event_timestamps.append(int(response_event['agreementLiquidatedByEvents'][x]['timestamp']))
    penaltyAccounts.append(response_event['agreementLiquidatedByEvents'][x]['penaltyAccount'])
    tokens.append(response_event['agreementLiquidatedByEvents'][x]['token'])

ids = list(map('-'.join, zip(penaltyAccounts, tokens)))

balanceUntilUpdatedAts = []
totalNetFlowRates = []
updatedAtTimestamps = []
token_names = []
for number, num in zip(block_numbers, ids):
    # Retrieving AccountTokenSnapshot:
    q_block = str(number - 1)
    query_token = gql(f"""
    query AccountTokenSnapshot {{
      accountTokenSnapshot(
        id:"{str(num)}"
        block: {{number:{q_block}}}
      ) {{token {{
      symbol}}
        balanceUntilUpdatedAt
        updatedAtTimestamp
        totalNetFlowRate
      }}
    }}
    """)

    response_token = client.execute(query_token)
    balanceUntilUpdatedAts.append(int(response_token['accountTokenSnapshot']['balanceUntilUpdatedAt']))
    totalNetFlowRates.append(int(response_token['accountTokenSnapshot']['totalNetFlowRate']))
    updatedAtTimestamps.append(int(response_token['accountTokenSnapshot']['updatedAtTimestamp']))
    token_names.append(response_token['accountTokenSnapshot']['token']['symbol'])

rds = []
rd_days = []
rd_hours = []
rd_minutes = []
rd_seconds = []
for event_timestamp, updatedAtTimestamp in zip(event_timestamps, updatedAtTimestamps):
    dt1 = datetime.datetime.fromtimestamp(updatedAtTimestamp)
    dt2 = datetime.datetime.fromtimestamp(event_timestamp)
    rd = dateutil.relativedelta.relativedelta(dt2, dt1)
    # rds.append (rd)
    rd_days.append(rd.days)
    rd_hours.append(rd.hours)
    rd_minutes.append(rd.minutes)
    rd_seconds.append(rd.seconds)

df_delta_1 = pd.DataFrame(
    {'days': rd_days,
     'hours': rd_hours,
     'minutes': rd_minutes,
     'seconds': rd_seconds
     })

df_delta_1['days_tomin'] = df_delta_1['days'] * 1440
df_delta_1['hours_tomin'] = df_delta_1['hours'] * 60
df_delta_1['sec_tomin'] = df_delta_1['seconds'] * 0.0166667
df_delta_1['delta'] = df_delta_1['days_tomin'] + df_delta_1['hours_tomin'] + df_delta_1['sec_tomin'] + df_delta_1[
    'minutes']
df_delta_1['delta'].median()  # minutes
previous = df_delta_1['delta'].median()  # minutes

# Compare

print(now, previous)
if now < previous:
    comparison = 'Yes, Improving ratio'
else:
    comparison = 'We are not improving'

df_token_time = (df_delta.groupby(['token'])['delta'].median()).sort_values(ascending=False)
df_token_time.to_frame()

# Remaining Balances at liquidation
df = pd.DataFrame(
    {'event_timestamp': event_timestamps,
     'pre_event_Timestamp': updatedAtTimestamps,
     'NetFlowRate': totalNetFlowRates,
     'pre_event_balance': balanceUntilUpdatedAts,
     'token': token_names
     })

df['balance'] = (df['pre_event_balance'] + (df['event_timestamp'] - df['pre_event_Timestamp']) * df[
    'NetFlowRate']) * 10 ** -18
media_balance = df['balance'].median()

eth_url = 'https://coinmarketcap.com/es/currencies/ethereum/'
HTML = requests.get(eth_url)
soup = BeautifulSoup(HTML.text, 'html.parser')
eth_price = (soup.find('div', attrs={'class': 'sc-16r8icm-0 kjciSH priceTitle'}).find('div', attrs={
    'class': 'priceValue'}).text).strip('$')
eth_US = float(eth_price.replace(',', ''))

balance_in_usd = media_balance * eth_US


# Most active penalty account
def most_frequent(List):
    return max(set(List), key=List.count)


gold_penalty_account = most_frequent(penaltyAccounts)

# Overall Statistic
ids_tosearch = list(dict.fromkeys(tokens))
names = []
totalOutflowRate = []
totalSupply = []

for id_tosearch in ids_tosearch:
    query_archive = gql(f"""
    {{
  tokenStatistic(id: "{id_tosearch}") {{
    token {{
      name
    }}
    totalOutflowRate
    totalSupply
  }}
}}
""")

    response_token = client.execute(query_archive)
    names.append(response_token['tokenStatistic']['token']['name'])
    totalOutflowRate.append(int(response_token['tokenStatistic']['totalOutflowRate']))
    totalSupply.append(int(response_token['tokenStatistic']['totalSupply']))

df_volume = pd.DataFrame(
    {'token': names,
     'owed': totalOutflowRate,
     'available': totalSupply
     })

df_volume['solvency'] = (df_volume['owed'] / df_volume['available'])
agg_solvency = (df_volume['owed'].sum() / df_volume['available'].sum())
df_volume.sort_values(by='solvency', ascending=False, inplace= True)

print ('data gathered. ready to plot')
# -----------------------------------------------

app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
                external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

tab_style = {"background": "darkred",'color': 'white',
             'text-transform': 'uppercase',
             'justify-content': 'center',
             'border': 'grey','border-radius': '10px',
             'font-size': '12px','font-weight': 600,
             'align-items': 'center','padding':'12px'}
tab_selected_style = {"background": "darkblue",'color': 'white',
                      'text-transform': 'uppercase',
                      'text-align': 'center',
                      'justify-content': 'center',
                      'border-radius': '10px',
                      'font-weight': 600,'font-size': '12px',
                      'align-items': 'center','padding':'12px'}

app.title = "Some metrics"

colors = ['primary', 'secondary', 'success', 'info', 'warning', 'danger', 'light', 'dark']

app.layout = html.Div(className='container pt-3', children=[
    html.H1(children='Some Superfluid metrics',
                style={'textAlign': 'center', 'color': 'darkblue',
                    'fontSize': '30px', 'fontWeight': 'bold'}
                ),
    html.Div(className='row', children=[
        html.Div(className='col-4', children=[
            html.H1(style=tab_selected_style, children=['Time']),
            html.Div([
                html.Br(),
                dbc.Alert([
                    html.H4("Solvency response time"),
                    html.P(transform_minutes(now))
                ]),
                html.Div(className='card mt-2', children=[
                    html.Div(className='card-body', children=[
                        html.H4('Tokens requiring longer time to resolve'),
                        html.Div([
                            html.Div(className='d-flex', children=[
                                dbc.Button(df_token_time.index[x], color=random.choice(colors), className="me-1 mb-1") for x in range(0,2)
                            ])
                        ])
                    ])
                ]),
                html.Div(className='mt-3', children=[
                    dbc.Card([
                        dbc.CardBody([
                            html.H4('Improved in relation to previous two weeks?'),
                            html.Hr(),
                            html.H4(comparison, className="card-title"),
                            html.Div(className='row', children=[
                                html.Div(className='col-6', children=[
                                    html.P(" Between: ", className="card-text")
                                ]),
                                html.Div(className='col-6', children=[
                                    html.P(datetime.datetime.fromtimestamp(1640991600).strftime("%m/%d/%Y, %H:%M:%S"), className="card-text")
                                ])
                            ]),
                            html.Div(className='row', children=[
                                html.Div(className='col-6', children=[
                                    html.P(" And: ", className="card-text")
                                ]),
                                html.Div(className='col-6', children=[
                                    html.P(datetime.datetime.fromtimestamp(1642067237).strftime("%m/%d/%Y, %H:%M:%S"), className="card-text")
                                ])
                            ])
                        ])
                    ])
                ])
            ])
        ]),
        html.Div(className='col-8', children=[
            html.H1(style=tab_selected_style, children=['Balance']),
            html.Div(className='row', children=[
                html.Div(className='col-8', children=[
                    html.Div([
                        html.Br(),
                        dbc.Alert(className='d-flex flex-column', children=[
                            html.H4("Media balance at liquidation (USD)"),
                            html.P(balance_in_usd),
                            html.Div(className='mt-auto d-flex justify-content-end', children=[
                                html.Div(className='d-flex', children=[
                                    html.P("ETH price USD", className=" pe-1 fw-bold border-end border-dark m-0"),
                                    html.P(eth_US,
                                        className="card-text ms-2",
                                    )
                                ])
                            ])
                        ]),
                        dbc.Alert(
                            [
                                html.H4("Most active penalty account!", className="alert-heading"),
                                html.P(gold_penalty_account)
                            ]
                        ),
                        dbc.Card(
                            dbc.CardBody([
                                html.H3('Overall statistic (ratio)'),
                                html.Hr(),
                                html.H6("owed / available", className="card-title"),
                                html.P(agg_solvency,
                                    className="card-text",
                                )
                            ])
                        )
                    ]),
                ]),
                html.Div(className='col-4', children=[
                    html.Br(),
                    html.Div([
                        html.Div(className='row mb-3', children=[
                            html.Div(className='col-4 d-flex align-items-center', children=[
                                html.P(className='m-0 text-align-center', children=[df_volume['token'].iloc[x]]),
                            ]),
                            html.Div(className='col-8 d-flex align-items-center', children=[
                                dbc.Button('{:.8E}'.format(df_volume['solvency'].iloc[x]), color="primary")
                            ])
                        ]) for x in range(0, 5)
                    ])
                ])
            ])
        ])
    ])
])

if __name__ == "__main__":
    app.run_server(debug=False)
