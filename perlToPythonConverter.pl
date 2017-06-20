#!/usr/bin/perl 
# A compiler takes a Perl script as input and outputs a Python script
# edited by Luke Yuan September 2016

@python = ();
$import_sys=0;
while ($line = <>) {
	chomp $line;
	push @python, translate_statement();
}
print @python;

sub translate_statement{
    # top translation function 
    check_package();
	if ($line =~ /^#!/ && $. == 1) {
		# translate #! line    
		return "#!/usr/local/bin/python3.5 -u \n";
	}
	elsif ($line =~ /^\s*#/ || $line =~ /^\s*$/) {
		# Blank & comment lines can be passed unchanged
		return "$line\n";
	} 
    elsif ($line =~ /print \"Enter a number\: \"\;/){
        $line = "sys.stdout.write(\"Enter a number: \")";
        return "$line\n";
    }
    elsif ($line =~ /^\s*print \"\$.* .*\"/){
        return complex_print();
    }
    elsif ($line =~ /^(\s*)exit/){
        $line = "$1sys.exit()";
        return "$line\n";
    }
	elsif ($line =~ /\$/){
		# Variables with $sign
		return translate_variables();
	}
    elsif($line =~ /@/){
        # arrays
        return translate_arrays();
    }
    elsif ($line =~ /^(\s*)print\s*(.*),\s*"\\n"/) {
		# line with print *** "\n" 
		return "$1print($2)\n";
	}
	elsif ($line =~ /^(\s*)print\s*"(.*)\\n"[\s;]*$/) {
		# Python's print adds a new-line character by default
		# so we need to delete it from the Perl print statement
        return "$1print(\"$2\")\n";
	} 
    elsif ($line =~ /^\s*if|while|else|elif|for|foreach/){
		return translate_control_statements();
	}
    elsif($line =~ /^\s*\}\s*$/){
        # if it is single } ending
    }
    elsif ($line =~ /printf/){
        return translate_printf();
    }
    elsif ($line =~ /^(\s*)print \"(.*)\"\;/){
        $line ="$1print (\"$2\", end=\"\")";
        return "$line\n";
    }
	else {
		# Lines we can't translate are turned into comments
		return "#$line\n";
	}
}

sub translate_variables {
	$line =~ s/\$//g;
	$line =~ s/\;//g;
	if ($line =~ /^(\s*)print\s*(.*),\s*"\\n"/) {
		# line with print *** "\n" 
		return "$1print($2)\n";
	}
	elsif ($line =~ /^(\s*)print\s*"(.*)\\n"[\s;]*$/) {
		# Python's print adds a new-line character by default
		# so we need to delete it from the Perl print statement	    
		return "$1print($2)\n";
	}
	elsif ($line =~ /^\s*if|while|else|elif|for|foreach/){
		return translate_control_statements();
	}
    elsif ($line =~ /^(\s*)chomp\s*(.*)/){
        return "$1$2 = $2.rstrip()\n";
    }
    elsif ($line =~ /<STDIN>/){
        $line =~ s/<STDIN>/float(sys.stdin.readline())/g;
        if ($line =~ /\sline/){
            $line =~ s/float\(sys.stdin.readline\(\)\)/sys.stdin.readline\(\)/g;
        }
        return "$line\n";
    }
    elsif($line =~ /^(\s*)(.*)\+\+/){
        return "$1$2 += 1\n";
    }
    elsif($line =~ /^(\s*)(.*)\-\-/){
        return "$1$2 -= 1\n";
    }
	else {
		return "$line\n";
	}
}

# recursive implementation which checks control statements loop syntax
sub translate_control_statements {
	my @control_perl = ();
    if ($line =~ /\seq\s/){
        $line =~ s/eq/==/g;
    }
    if ($line =~ /\sne\s/){
        $line =~ s/ne/!=/g;
    }
    if ($line =~ /^(\s*)while\s*\((.*)=\s*\<STDIN\>/){
        $line="$1for $2in sys.stdin:\n";
        push @control_perl, $line;
    }
    elsif ($line =~ /^(\s*)while\s*\((.*)=\s*\<\>/){
        splice @python, 1, 0, "import fileinput\n";
        $line= "$1for $2in fileinput.input():\n";
        push @control_perl, $line;
    }
	elsif ($line =~ /^(\s*)(if|while|elif)\s*\((.*)\)/){
		$control_type=$2;
		$control_type = "elif" if $control_type eq "elsif";
		$line= "$1$control_type $3:\n";
		push @control_perl, $line;
	}
    elsif ($line =~ /^(\s*)foreach\s*(.*)\s*\((.*)\.\.\#ARGV/){
        # dealing with $#ARGV
        $range_head=$3+1;
        $line= "$1for $2in range(len(sys.argv) - $range_head):\n";
        push @control_perl, $line;
    }
    elsif ($line =~ /^(\s*)foreach\s*(.*)\s*\((.*)\.\.(.*)\)/){
        # # dealing with other range
        $range_end=$4+1;
        $line= "$1for $2in range($3,$range_end):\n";
        push @control_perl, $line;
    }
    elsif ($line =~ /^(\s*)foreach\s*(.*)\s*\((.*)\)/){
        $line= "$1for $2in $3:\n";
        push @control_perl, $line;
    }
    elsif ($line =~ /^(\s*)else\s*\{/){
        $line = "else :\n";
        push @control_perl, $line;
    }
	while ($line = <> ){
		chomp $line;
		# continually read lines until reaching closing brackets
		if ($line =~ /\}/){
			last;
		}
		elsif ($line =~ /^(\s*)next/){
			$line = "$1continue\n";
			push @control_perl, $line;
		}
		elsif ($line =~ /^(\s*)last/){
			$line = "$1break\n";
			push @control_perl, $line;
		}
		else {
			push @control_perl, translate_statement();
		}
	}
    if ($line =~ /^(\s*)\}\s*else\s*\{/){
        $line = "$1else:\n";
        push @control_perl, $line;
    }
    elsif ($line =~ /^(\s*)else\s*\{/){
        $line = "$1else:\n";
        push @control_perl, $line;
    }
    elsif ($line =~ /^(\s*)\}\s*elsif\s*\((.*)\)/){
        $line = "$1elif $2:\n";
        $line =~ s/\$//g;
        push @control_perl, $line;
        @extra_elif= complex_elif();
        push @control_perl,@extra_elif;
    }
	return @control_perl;
}

sub check_package{
    # check for packages, if we need that put it after interpreter statement
    if ($line =~ /(ARGV|STDIN|exit)/ && $import_sys==0 ){
        $import_sys=1;
        splice @python, 1, 0, "import sys\n";
    }
    if ($line =~ /\@ARGV/){
        $line =~ s/\@ARGV/sys.argv[1:]/g;
    }
    if ($line =~ /(.*)\$ARGV\[(.*)\](.*)/){
        $line = "$1sys.argv[$2 + 1]$3";
    }
    if ($line =~ /join\((.*),(.*)\)/){
        $line =~ s/join\((.*),(.*)\)/$1\.join($2)/g;
    }
    if ($line =~ /^(\s*)\$(.*)\=\~ s\/\[(.*)]\/(.*)\//){
        # regexes s///
        splice @python, 1, 0, "import re\n";
        $line = "$1\$$2= re.sub(r'[$3]','$4',$2)";
    }
}

sub complex_print(){
    if ($line =~ /^(\s*)print \"\$(.*) (.*)\\n"/){
        $line ="$1print(\"%s $3\" % $2)";
        return "$line\n";
    }
}

sub complex_elif{
    my @control_perl = ();
    while ($line = <> ){
        chomp $line;
        # continually read lines until reaching closing brackets
        if ($line =~ /\}/){
            last;
        }
        elsif ($line =~ /^(\s*)next/){
            $line = "$1continue\n";
            push @control_perl, $line;
        }
        elsif ($line =~ /^(\s*)last/){
            $line = "$1break\n";
            push @control_perl, $line;
        }
        else {
            push @control_perl, translate_statement();
        }
    }
    if ($line =~ /^(\s*)\}\s*else\s*\{/){
        $line = "$1else:\n";
        push @control_perl, $line;
    }
    elsif ($line =~ /^(\s*)else\s*\{/){
        $line = "$1else:\n";
        push @control_perl, $line;
    }
    elsif ($line =~ /^(\s*)\}\s*elsif\s*\((.*)\)/){
        $line = "$1elif $2:\n";
        $line =~ s/\$//g;
        push @control_perl, $line;
        @extra_elif= complex_elif();
        push @control_perl,@extra_elif;
    }
    return @control_perl;
}

sub translate_arrays(){
    # manipulating arrays such as push, pop, shift commands
    if ($line =~ /^(\s*)\@(.*)\=\s*\((.*)\)/){
        $line = "$1$2= \[$3\]";
        return "$line\n";
    }
    elsif($line =~ /^(\s*)push \@(.*),\s*(.*);/){
        $line = "$1$2.append($3)";
        return "$line\n";
    }
    elsif($line =~ /^(\s*)pop \@(.*);/){
        $line = "$1$2.pop()";
        return "$line\n";
    }
    elsif($line =~ /^(\s*)pop \@(.*);/){
        $line = "$1$2.pop()";
        return "$line\n";
    }
    elsif($line =~ /^(\s*)unshift \@(.*),\s*(.*);/){
        $line = "$1$2.insert(0,$3)";
        return "$line\n";
    }
    elsif($line =~ /^(\s*)shift \@(.*);/){
        $line = "$1$2.pop(0)";
        return "$line\n";
    }
    elsif ($line =~ /^(\s*)\@.*reverse\s*\(\@(.*)\);/){
        $line = "$1$2.reverse()";
        return "$line\n";
    }
    elsif ($line =~ /^(\s*)print @(.*),/){
        $line = "$1print ($2)";
        return "$line\n";
    }
    else {
		# Lines we can't translate are turned into comments
		return "#$line\n";
	}
}

sub translate_printf(){
    if ($line =~ /^(\s*)printf \"%(.).*\",(.*);/){
        $line = "$1print (\"\%$2\" \% $3)";
        return "$line\n";
    }
}