<!DOCTYPE html>
<html lang="hu">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{{title or 'PiCam'}}</title>
    <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.5/css/bootstrap.min.css" />
    <link rel="stylesheet" type="text/css" href="/static/content/site.css" />
    <script src="https://cdnjs.cloudflare.com/ajax/libs/modernizr/2.8.3/modernizr.min.js"></script>
</head>
<body>
    <div class="navbar navbar-inverse navbar-fixed-top">
        <div class="container">
            <div class="navbar-collapse collapse">
                <ul class="nav navbar-nav">
                    <li><a href="/home"><i class="glyphicon glyphicon-flash"></i> Események</a></li>
                    <li><a href="/view"><i class="glyphicon glyphicon-film"></i> Monitor</a></li>
                </ul>
            </div>
        </div>
    </div>
    <div class="container body-content">
        {{!base}}
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/2.1.4/jquery.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/3.3.5/js/bootstrap.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/respond.js/1.4.2/respond.min.js"></script>
</body>
</html>

