import dash

app = dash.Dash(__name__, 
	suppress_callback_exceptions=True, 
	meta_tags=[{"name": "viewport", "content": "width=device-width"}]
	)

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>COVID-19 Tracker</title>
        <meta property="og:title" content="COVID-19 Tracker">
        <meta property="og:image" content="assets/screenshot.png">
        <meta name="description" property="og:description" content="An interactive mini-dashboard built and deployed by me in Python,tracking COVID-19 spread in near real-time">
        <meta name="author" content="Anthony S N Maina">
        <link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png">
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png">
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png">
        <link rel="manifest" href="/site.webmanifest">
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

