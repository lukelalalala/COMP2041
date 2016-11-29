#!/usr/bin/perl -w
# A Perl script which prints courses that are offered online
# and fully online specifically at UNSW 

use List::MoreUtils qw(uniq);

$year = 2017;
$url_base = "timetable.unsw.edu.au";
@url_base_levelOne = ("$url_base/$year/KENSUGRDU1.html",
"$url_base/$year/KENSUGRDU1C.html","$url_base/$year/KENSUGRDU1B.html");

foreach $url_levelOne (@url_base_levelOne) {
    open my $f, "wget -q -O- $url_levelOne|" or die;
    while ($line = <$f>) {
        # looking for subject code
        if ($line =~ /html\">([A-Z]{4})<\/a><\/td>/ ) {
            push @subjects, $1;
        }
    }
    close $f;
	foreach my $subject (sort @subjects) {
		my $url_levelTwo = $url_levelOne;
		$url_levelTwo =~ s/\.html//;
		$url_levelTwo = $url_levelTwo.$subject.".html";
		open my $f, "wget -q -O- $url_levelTwo|" or die;
		while ($line = <$f>) {
        # looking for course code
			if ($line =~ /html\">([A-Z]{4}\d{4})<\/a><\/td>/ ) {
				push @courses, $1;
			}
		}
		close $f;
	}
	undef @subjects;
}

# we got the course list, searching for keywords "online"
foreach my $course (sort @courses){
	my $url_levelThree = "$url_base/$year/$course.html";
	open my $f, "wget -q -O- $url_levelThree|" or die;
	while ($line = <$f>) {
		if ($line =~ /online/ ) {
			push @online_courses,$course;
		}
		if ($line =~ /(fully|entirely) online/ ) {
			push @fully_online_courses,$course;
		}
	}
	close $f;
}

print "These courses are offered online: \n";
my @unique_online_courses = uniq @online_courses;
foreach $online_course (sort @unique_online_courses){
	print "$online_course\n";
}

print "Specifically, these courses are offered fully online: \n";
my @unique_fully_online_courses = uniq @fully_online_courses;
foreach $fully_online_course (sort @unique_fully_online_courses){
	print "$fully_online_course\n";
}