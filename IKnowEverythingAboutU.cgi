#!/usr/bin/perl -w
# A CGI script that gets user's location

use CGI qw/:all/;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);

print <<eof;
Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
<head>
<title>I KNOW EVERYTHING ABOUT YOU</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="bootstrap/css/bootstrap.min.css">    
    <script src="bootstrap/js/bootstrap.min.js"></script>
</head>

<body>
<div class="jumbotron text-center">
    <h1>I KNOW EVERYTHING ABOUT YOU</h1>
    <p>And you know what will happen</p>
</div>
eof

warningsToBrowser(1);
if (defined param("buttonTwo")) {
    print <<eof;
    <div class="container">
        <h2> That is not possible! </h2>
        <h2> Do you even know your IP address? </h2>
        <h2> Stop lying LOL </h2>
    </div>
eof
} elsif (defined param("buttonOne")) {
	print <<eof;
    <div class="container">
        <h2> Looks like u trust me, and surely I know more </h2>
eof
    $page = "http://ip.cn/index.php?ip=".$ENV{'REMOTE_ADDR'};
    open $f, "wget -q -O- $page|" or die;
    
    while ($line = <$f>) {
        if ($line =~ /GeoIP: (.*),/ ) {
            $location = $1;
        }
    }
    close $f;
    print <<eof;  
    <h2 class="alert alert-success" > I know you are in: <h2>
    <h4>   $location </h4>
    <form method="post" action="">
        <input type="submit" class="btn btn-primary btn-md" name="buttonThree" value="Okay! So...">
    </form>
    </div>
eof
} elsif (defined param("buttonThree")) {
    print <<eof;
    <div class="container">
        <h2> Well, it is not that easy to get ur location and please dont take this as a scam. </h2>
        <h2> Oh please, don't hesitate to message me </h2>
        <h1> NOW </h1>
    </div>
eof
} else {
print <<eof;
<div class="container">
    <dl>
    <dt>You are running at IP address: </dt>
    <dd>$ENV{'REMOTE_ADDR'}</dd>
    <br>
    <dt>
    You are using: </dt>
    <dd>$ENV{'HTTP_USER_AGENT'}</dd>
    </dl>
    <div class="alert alert-warning">
    <strong>Warning!  </strong>AM I RIGHT?
    </div>
    <form method="post" action="">
        <input type=hidden name="x" value="$hidden_variable">
        <input type="submit" class="btn btn-primary btn-md" name="buttonOne" value="Yes">
        <input type="submit" class="btn btn-primary btn-md" name="buttonTwo" value="No">
    </form>
eof
}

print <<eof;
    </div>
    </body>
    </html>
eof
