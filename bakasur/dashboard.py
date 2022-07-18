import pandas as pd
import datapane as dp
import altair as alt
from datetime import datetime

from bakasur.constants import REPORT_PATH

pd.options.mode.chained_assignment = None


def display(order_data, order_details_data):
    order_data['order_datetime'] = pd.to_datetime(order_data.order_datetime)
    order_data['weekday'] = order_data.order_datetime.dt.day_name()
    days_since_last_order = pd.to_datetime(datetime.today()) - order_data.order_datetime.max()

    weekday_dist_df = order_data['weekday'].value_counts().rename_axis('weekday').reset_index(name='counts')
    weekday_dist_df['weekday'] = pd.Categorical(weekday_dist_df['weekday'],
                                                categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                                                            'Saturday', 'Sunday'],
                                                ordered=True)
    weekday_dist_df = weekday_dist_df.sort_values('weekday').reset_index(drop=True)

    spends_per_month_df = order_data[["order_datetime", "order_val"]]
    spends_per_month_df["order_count"] = 1
    spends_per_month_df = spends_per_month_df.resample("M", on="order_datetime").sum().reset_index()
    spends_per_month_df = spends_per_month_df.assign(month_year=lambda x: x['order_datetime'].dt.strftime("%b-%y"))

    top_restaurants_df = order_details_data['restaurant_name'].value_counts().rename_axis('restaurant').reset_index(
        name='num_ordered').query("num_ordered > 3")

    most_ordered_item_df = order_details_data["order_name"].value_counts().rename_axis('item').reset_index(
        name='num_ordered').query("num_ordered >= 2")

    most_ordered_item_chart = alt.Chart(most_ordered_item_df).mark_bar().encode(
        x=alt.X('num_ordered', sort=None, title="Number of orders"),
        y=alt.Y('item', sort=None, title="Item"),
        color=alt.Color('num_ordered',
                        scale=alt.Scale(scheme='teals'))
    ).properties(title="My most ordered dishes")

    top_restaurants_chart = alt.Chart(top_restaurants_df).mark_bar().encode(
        x=alt.X('num_ordered', sort=None, title="Number of orders"),
        y=alt.Y('restaurant', sort=None, title="Restaurant"),
        color=alt.Color('num_ordered',
                        scale=alt.Scale(scheme='teals'))
    ).properties(title="Restaurants I frequently order from")

    base = alt.Chart(spends_per_month_df).mark_bar().encode(
        x={
            "field": "order_val",
            "type": "quantitative",
            "title": "Spends per month (in €)"
        },
        y={
            "field": "month_year",
            "type": "ordinal",
            "sort": None,
            "title": "Month-Year"
        }
    )

    spends_chart = base.mark_bar().encode(
        color=alt.Color('order_val',
                        scale=alt.Scale(scheme='lightmulti'))
    ).properties(title="Money spent and orders placed each month")

    text = base.mark_text(
        align='left',
        baseline='middle',
        dx=3
    ).encode(
        text='order_count'
    )

    alt_chart = alt.Chart(weekday_dist_df).mark_bar().encode(
        x={"field": "weekday",
           "type": "ordinal",
           "sort": ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                    'Saturday', 'Sunday'],
           "title": "Weekday"},
        y={"field": "counts",
           "type": "quantitative",
           "title": "Orders per day"},
        color=alt.Color('counts',
                        scale=alt.Scale(scheme='blues'))).properties(title="When do I order most frequently?")
    dp.Report(
        dp.Group(
            dp.BigNumber(
                heading="Days since my last order", value=days_since_last_order.days),
            dp.BigNumber(heading="Total number of orders", value=len(order_data)),
            columns=2
        ),
        dp.Group(
            dp.Plot(alt_chart),
            dp.Plot((spends_chart + text).properties(height=400)),
            columns=2
        ),
        dp.Group(
            dp.Plot(top_restaurants_chart),
            dp.Plot(most_ordered_item_chart),
            columns=2
        )
    ).save(open=True, path=REPORT_PATH)
