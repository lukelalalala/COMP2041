#!/usr/bin/perl -w

# Implementing a simple but fully functional social media web site
# Login with z3413158 and internet
# written by Luke Yuan z5042615 October 2016

use File::Basename;
use Data::Dumper qw(Dumper);
use CGI qw/:all/;
use CGI::Carp qw/fatalsToBrowser warningsToBrowser/;


sub main() {
    # print start of HTML ASAP to assist debugging if there is an error in the script
    print page_header();
    # Now tell CGI::Carp to embed any warning in HTML
    warningsToBrowser(1);
    # define some global variables
    $debug = 1;
    $users_dir = "dataset-small";
    # txt file to store login flags
    open F, "login.txt" or die "can not open $details_filename: $!";
    my $login_flag = <F>;
    
    if(defined (param("logout"))){
        open FI, '>', "login.txt" or die "Can't open > $filename: $!";
        print FI "0";
        close FI;
    }
    if ($login_flag==0){
        login();
    }
    if(defined (param("logout"))){
        $login_flag=0;
    }
    if ($login_flag==1){
        print user_page();
        print page_trailer();
    }

}

# Show unformatted details for user "n".
# Increment parameter n and store it as a hidden variable
sub user_page {
    my $n = param('n') || 0;
    my @users = sort(glob("$users_dir/*"));
    my $user_to_show  = $users[$n % @users];
    check_search();
    
    # check if any name button has previously been clicked
    $user_to_show=jumping_page($user_to_show,\@users);
    my $details_filename = "$user_to_show/user.txt";
    # display the user's image if there is one otherwise we have a default profile image
    my $user_image= "$user_to_show/profile.jpg"; 
    open my $p, "$details_filename" or die "can not open $details_filename: $!";
    
    # Private information
    while ($line = <$p>){
        if ($line !~ /email/ && $line !~ /home_latitude/ && $line !~ /home_longitude/ && $line !~ /password/ && $line !~ /course/){
            push @details, $line;
        }
		if ($line =~ /mates=(.*)/){
			$user_mates=user_mate($1);
		}
    }
    @details = sort @details;
    $details = join "<br>", @details; 
    close $p;
    
    # dealing with posting
	$file_content = param('whatsnew');
	# sanitize posts by removing < characters, disabling any HTML tag
	$file_content =~ s/</&lt;/g;
	if (param('whatsnew') && defined $file_content){
		making_post($user_to_show);
	}
    # displaying posts, comments and replies
	posts($user_to_show);
	my @sorted_post = print_post();
    my $posts= join("",@sorted_post);
    
    my $next_user = $n + 1;
    # after all we return all the html contents
    return <<eof
<div class="container">
	<form class="form-horizontal" method="POST" action="">
		<div class="form-group">
			<label class="control-label col-sm-1" for="whatsnew">What's new:</label>
			<div class="col-sm-9">
				<textarea class="form-control" rows="3" name="whatsnew" id="whatsnew" placeholder="What's on your mind"></textarea>
			</div>
			<div class="col-sm-2">
                <input type="submit" value="Post" class="btn btn-default">
            </div>
		</div>
	</form>
    <div class="row">
        <div class="col-sm-4">
            <img src="$user_image" height= "250" width="250" alt="No profile" onerror="this.src='default_image.jpeg';" />
        </div>
        <div class="col-sm-8">
            $details
        </div>
    </div>
</div>

<div class="container">
    <form method="POST" action="">
        <input type="hidden" name="n" value="$next_user">
        <input type="submit" value="Next user" class="btn btn-primary btn-md">
    </form>
</div>

<div class="container">
    <h3> Friends </h3>
    <form method="POST" action="">
        $user_mates
    </form>
</div>

<div class="container">
	<h3> Timeline </h3>
    $posts
</div>

eof
}

# HTML placed at the top of every page
# import Bootstrap
sub page_header {
    return <<eof
Content-Type: text/html;charset=utf-8

<!DOCTYPE html>
<html lang="en">
<head>
<title>matelook</title>
<!-- Bootstrap CDN -->
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
<script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
</head>
<body>
<div class="container">
    <form method="post" action="">
        <input type="submit" name="logout" value="logout">
    </form>
    <div class="jumbotron text-center">
        <h1>Luke's Matelook</h1>
    </div>
    <form class="form-horizontal" method="POST" action="">
        <div class="form-group">
            <label class="control-label col-sm-1" for="user_name">Names:
            </label>
            <div class="col-sm-9">
                <input type="text" class="form-control" name="search_name" id="user_name" placeholder="Enter user name">
            </div>
            <div class="col-sm-2">
                <input type="submit" name="search_name_button" value="Search" class="btn btn-default">
            </div>
        </div>
        <div class="form-group">
            <label class="control-label col-sm-1" for="user_post">Posts:
            </label>
            <div class="col-sm-9">
                <input type="text" class="form-control" name="search_post" id="user_post" placeholder="Enter user post">
            </div>
            <div class="col-sm-2">
                <input type="submit" name="search_post_button" value="Search" class="btn btn-default">
            </div>
        </div>
    </form>
</div>
eof
}

# HTML placed at the bottom of every page
# It includes all supplied parameter values as a HTML comment
# if global variable $debug is set
sub page_trailer {
    my $html = "";
    $html .= join("", map("<!-- $_=".param($_)." -->\n", param())) if $debug;
    $html .= end_html;
    return $html;
}

sub check_search{
    # searching for a user whose name containing a specified substring
    if (defined param('search_name_button')){
        my @users = sort(glob("$users_dir/*"));
        my @search_list;
        my $x = param(search_name);
        
        # loops to search every single user
        foreach my $u (@users){
            my $details_filename = "$u/user.txt";
            open my $p, "$details_filename" or die "can not open $details_filename: $!";
            while ($line = <$p>){
                if ($line =~ /full_name=(.*)/){
                    my $sub =$1;
                    
                    if ($sub =~ /$x/){
                        # grep the name as required
                        push @search_list, $sub;
                        # trying to get zid
                        open my $p, "$details_filename" or die "can not open $details_filename: $!";
                        
                        while ($line = <$p>){
                            if ($line =~ /zid=(.*)/){
                                my $sub_zid=$1;
                                # after we get the user push the image and their names to the array
                                push @serach_list, "<img src=\"".$users_dir."/$sub_zid/profile.jpg"."\" class=\"img\-thumbnail\" width=\"40\" height=\"40\" onerror=\"this.src=\'default_image.jpeg\'\;\" />";
                                push @serach_list,"<input type=\"submit\" name=\"$sub_zid\" value=\"$sub\" class=\"btn btn-outline-info btn-sm\"> ";
                            }
                        }
                    }
                }
            }
        }
        my $user_searching= join("",@serach_list);
		my $m= scalar @search_list;
        print <<eof;
<div class="container">
    <form method="POST" action="">
	<p class="bg-info">$m matches found </p>
    $user_searching
    </form>
</div>
eof
    }
    
    # similar to names, searching for posts
    if (defined param("search_post_button")){
        my @users = sort(glob("$users_dir/*"));
        my @search_list;
        my $x = param("search_post");
        # loops to search every single user
        foreach my $u (@users){
            my @users_posting = sort(glob("$u/posts/*"));
            
            # loops to search every single post
            foreach my $v (@users_posting){
                my $details_filename = "$v/post.txt";
                open my $p, "$details_filename" or die "can not open $details_filename: $!";
                while ($line = <$p>){
                    if ($line =~ /message=(.*)/){
                        my $sub =$1;
                        # grep the message as required
                        if ($sub =~ /$x/){                         
                            # trying to get zid
                            open my $p, "$details_filename" or die "can not open $details_filename: $!";
                            
                            while ($line = <$p>){
                                if ($line =~ /from=(.*)/){
                                    my $sub_zid=$1;
                                    my $sub_zid_name= get_user_name($sub_zid);
                                    # after we get the user push the image and their names to the array
                                    push @serach_list, "<img src=\"".$users_dir."/$sub_zid/profile.jpg"."\" class=\"img\-thumbnail\" width=\"40\" height=\"40\" onerror=\"this.src=\'default_image.jpeg\'\;\" />";
                                    push @serach_list,"<input type=\"submit\" name=\"$sub_zid\" value=\"$sub_zid_name\" class=\"btn btn-outline-info btn-sm\"> $sub <br>";
                                    
                                }
                            }
                        }
                    }
                }
            }
        }
        my $user_searching= join("",@serach_list);
		my $m= scalar @search_list;
        print <<eof;
<div class="container">
    <form method="POST" action="">
    $user_searching
    </form>
</div>
eof
    }
}

# import zid to get name
sub get_user_name{
    my $z =shift;
    $z=$users_dir."/$z/user.txt";
    # open the users txt file to find name according to their zid
    open my $p, "$z" or die "can not open $z: $!";
    
    while ($line = <$p>){
        if ($line=~ /full_name=(.*)/){
            my $user_name=$1;
			return $user_name;
        }
    }
}

# Display mates' thumbnail image 
# Using submit button and making it like a link
sub user_mate{
	my $line=shift;
	$line =~ s/[\[\]]//g;
	$line =~ s/ //g;
	my @zid=split /,/,$line;
	my @user_mates;
    
	foreach my $z (@zid){
        my $user_name = get_user_name($z);
		posts($users_dir."\/".$z);
		push @user_mates, "<img src=\"".$users_dir."/$z/profile.jpg"."\" class=\"img\-thumbnail\" width=\"80\" height=\"80\" onerror=\"this.src=\'default_image.jpeg\'\;\" />";
        push @user_mates,"<input type=\"submit\" name=\"$z\" value=\"$user_name\" class=\"btn btn-outline-info\"> ";
        push @user_mates,"&nbsp&nbsp";
    }
    
	my $user_mate= join("",@user_mates);
	# return elements formatting like <img src="dataset-medium/z3275760/profile.jpg" class="img-thumbnail" width="50" height="50">
	# and <input type="submit" name="z348885" value="z3485885" class="btn btn-primary btn-md"> <br>
    return $user_mate;
}

# if the user which is clicked appears in our dataset,
# we change the page to a new one
sub jumping_page{
    my $user_to_show=shift;
    my $refzid= shift;
    my @zid = @{$refzid};
    
    foreach my $z (@zid){
        $z =~ s/$users_dir\///;
        if (defined param($z)) {
            return $users_dir."/$z";
        }
    }
    # if not defined we return the original one
    return $user_to_show;
}

# to create a post, in perl we need to make a folder then a file
sub making_post{
	my $user_to_show=shift;
	my $z_user=$user_to_show;
	$z_user=~ s/.*\///;
	$user_to_show=$user_to_show."/posts";
	my @array = sort(glob("$user_to_show/*"));
	my $post_num= scalar @array;
	my $folder_path=$user_to_show."/".$post_num;
    
    # create folder 
	mkdir $folder_path;
	my $filename = $folder_path."/"."post.txt";
    
    # write to the new file
	open FI, '>', $filename or die "Can't open > $filename: $!";
	print FI "from=".$z_user,"\n";
	print FI "time=";
	# internal function that getting times 
	($sec,$min,$hour,$mday,$mon,$year) = localtime();
	# the year is always displayed as 116...
	$year=~ s/\d//;
	# displayed month is one earlier.......
	$mon=$mon+1;
	printf FI ("20%d-%02d-%02dT%02d:%02d:%02d+0000\n", $year,$mon,$mday,$hour, $min, $sec);
	print FI "message=".$file_content,"\n";
	close FI;
}

# function that import post content into a hash
sub posts{
	my $user_to_show=shift;
	my $zid= $user_to_show;
	$zid=~ s/.*\///;
	my $user_name=get_user_name($zid);
	my @user_posts= sort(glob("$user_to_show/posts/*"));
    
	foreach my $post_dir (@user_posts){
        my $post_file="$post_dir/post.txt";
        open $F, "$post_file" or die "can not open $post_file: $!";
        
        # grep time and message from post.txt
        while ($line =<$F>){
            # substitue any \n to <br> in html
			$line =~ s/\\n/<br>/g;
			$line =~ s/\+0000//g;
            if ($line =~ /message=(.*)/){
                $message=$1;
            }
            if ($line =~ /time=(.*)/){
                $time=$1;
            }
        }
        $user_post_hash{$time}{$zid}=$message;
		comment_post($post_dir,$message);
    }
}

# function that import comment content into a hash
sub comment_post{
	my $post_dir=shift;
	my $message=shift;
	my @user_comment= sort(glob("$post_dir/comments/*"));
	foreach my $c (@user_comment){
        my $comment_file="$c/comment.txt";
        open $F, "$comment_file" or die "can not open $comment_file: $!";
        
        # grep time and message from post.txt
        while ($line =<$F>){
			$line =~ s/\\n/<br>/g;
			$line =~ s/\+0000//g;
            
            if ($line =~ /message=(.*)/){
                $m=$1;
				my @array = split(/\s+/,$m);
				
                foreach my $w (@array){
                    # convert zid to real names
					if ($w =~ /^z\d\d\d\d\d\d\d$/){
						$w="<u>".get_user_name($w)."</u>";
					}
				}
				$m = join(" ",@array);
            }
            
            if ($line =~ /from=(.*)/){
                $t=$1;
            }
        }
		$comment{$message}{$t}=$m;
		reply_post($c,$m);
    }
}

# similar to post and comment function
sub reply_post{
	my $post_dir=shift;
	my $message=shift;
	my @user_reply= sort(glob("$post_dir/replies/*"));
	foreach my $r (@user_reply){
        my $reply_file="$r/reply.txt";
        open $F, "$reply_file" or die "can not open $reply_file: $!";
        
        # grep time and message from post.txt
        while ($line =<$F>){
			$line =~ s/\\n/<br>/g;
			$line =~ s/\+0000//g;
            
            if ($line =~ /message=(.*)/){
                $mmm=$1;
				my @array = split(/\s+/,$mmm);
				
                foreach my $w (@array){
                    # convert zid to real names
					if ($w =~ /^z\d\d\d\d\d\d\d$/){
						$w="<u>".get_user_name($w)."</u>";
					}
				}
				$mmm = join(" ",@array);
            }
            
            if ($line =~ /from=(.*)/){
                $ttt=$1;
            }
        }
		$reply{$message}{$ttt}=$mmm;
    }
}

sub print_post{
	my @sorted_user;
    # reverse the hash in accordance with time
    foreach my $posting_time (reverse sort keys %user_post_hash ){
    	
        # the posts displays like time...content...then new line
        foreach my $zz (sort keys %{$user_post_hash{$posting_time}}){
			my $user_n=get_user_name($zz);
            push @sorted_user,"<input type=\"text\" class=\"form-control input-sm\" rows=\"1\" name=\"new_comment\" id=\"new_comment\" placeholder=\"Comment\"></textarea><br>\n";
			push @sorted_user, "<p><img src=\"".$users_dir."/$zz/profile.jpg"."\" class=\"img\-thumbnail\" width=\"50\" height=\"50\" onerror=\"this.src=\'default_image.jpeg\'\;\" />".
			"&nbsp&nbsp$user_n </p>";
			push @sorted_user, "<p class=\"bg-primary\"> posted on &nbsp&nbsp&nbsp". $posting_time."<br>\n";
			push @sorted_user, $user_post_hash{$posting_time}{$zz}."</p>";
			my $x=$user_post_hash{$posting_time}{$zz};
			
            # push comment after each post
			foreach my $id (sort(keys %{$comment{$x}})) {
				my $id_name=get_user_name($id);
				push @sorted_user, "<img src=\"".$users_dir."/$id/profile.jpg"."\" hspace=\"20\" class=\"img\-thumbnail\" width=\"30\" height=\"30\" onerror=\"this.src=\'default_image.jpeg\'\;\" />".
				"$id_name commented: ".$comment{$x}{$id}."<br>";
				my $y=$comment{$x}{$id};
				
                # push replies after each comment
                foreach my $id (sort(keys %{$reply{$y}})) {
					my $id_name=get_user_name($id);
					push @sorted_user, "<img src=\"".$users_dir."/$id/profile.jpg"."\" hspace=\"40\" class=\"img\-thumbnail\" width=\"30\" height=\"30\" onerror=\"this.src=\'default_image.jpeg\'\;\" />".
					"$id_name replied: ".$reply{$y}{$id}."<br>";
				}
			}
		}
    }
    return @sorted_user;
}

# login page 
sub login{
    $username = param('username') || '';
    $password = param('password') || '';

    if ($username && $password) {
        check_login();
    } else {
        print start_form, "\n";
        if ($username) {
            print hidden('username');
        } else {
            print "Username:<br>\n", "<input type=\"text\" class=\"form-control\" name=\"username\" >", "\n";
        }
        if ($password) {
            print hidden('password');
        } else {
            print "Password:<br>\n", "<input type=\"password\" class=\"form-control\" name=\"password\">", "\n";
            
        }
        print submit(value => Login), "\n";
        print end_form, "\n";
        print "Login with z3413158 and internet";
    }
}

sub check_login{
    if (open F, '<', "$users_dir/$username/user.txt") {
        
        while (my $line = <F>){
            if ($line =~ /password=(.*)/){
                $correct_password = $1;
            }
        }
        chomp $correct_password;
        # login success we change the login flag to 1
        if ($correct_password eq $password){
            print "$username authenticated.<br>Please refresh the page.";
            open FI, '>', "login.txt" or die "Can't open > $filename: $!";
            print FI "1";
            close FI;
            return;
        }
        else {
            print "Incorrect password!\n";
        }
    }
    else{
        print ("Unknown username!");
    }
}

main();
