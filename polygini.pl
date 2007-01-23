#!/usr/bin/perl
## polygini.pl written by rishab@dxm.org v1.07 (28/7/03)
## copyright (c) 2003 rishab aiyer ghosh. distributed under the GNU GPL v2.0
## description: outputs gini coefficient and lorenz curve data
## CHANGELOG: v1.0 - 14/5/03. 
##	      v1.01 - added -id option
##	      v1.02 - fixed -id option, was mangling arguments and output.
##	      v1.03 - added -nocomment option and comment feature for input
##	      v1.04 - fixed NAN printing so that with -id, id is also printed
##	      v1.05 - hack to fix DIV0 error on buggy input (all-zero) data
##	      v1.06 - 19/7/03 improved hack and added -zeromsg option
##	      v1.07 - 28/7/03 added -count and -sum options
## polygini.pl [-precision PREC] [-zero PAD] [-scale SCALE] [-nogini] [-lorenz]
##             [-ntiles NTILES] [-nan [exit|eof|skip|msg]] [-id] 
##	       [-comment [none|copy|skip]] [-zeromsg] [-count] [-sum]
##	       [inputfile]
## polygini.pl --help 
##     for instructions (or read the $helptext variable below)
##

$helptext = <<'EOT';
 polygini.pl written by rishab@dxm.org, v1.07 (28/7/03)
 copyright (c) 2003 rishab aiyer ghosh. distributed under the GNU GPL v2.0
 
 description:  outputs gini coefficient and lorenz curve data

 polygini.pl --help  (for these instructions)

 polygini.pl [-precision PREC] [-zero PAD] [-scale SCALE] [-nogini] [-lorenz] 
             [-ntiles NTILES] [-nan [exit|eof|skip|msg]] [-id] 
	     [-comment [none|copy|skip]] [-zeromsg] [-count] [-sum] 
	     [inputfile]  

 assumes comma-separated numerical input data in inputfile or STDIN
 each row is a separate data set

 output is comma-separated numerical data (to STDOUT), with each output
 row containing the output for the corresponding input row, in fields following
 the sequence:
 		ID field (if -id flag set)
		the gini coefficient (unless -nogini, in which case 
			no gini coefficient is output)
		count (if -count flag): number of input data elements, same as
			the number of lorenz data elements (if output).
		sum (if -sum flag): sum of input data elements. 
		next fields contain input data transformed to a form
			suited for lorenz curves (i.e. divided by sum of
			data values and multiplied by SCALE)
		next fields contain NTILES ntiles (e.g. -ntiles 10 outputs
			deciles). note that if count < NTILES, the value and
			number of the ntiles fields is undefined and the fields
			should be ignored.
 the output sequence is always gini,lorenz,ntiles - though lorenz and
 ntiles are output only if the option is set on the command line
 OPTIONS:
 	-precision PREC	digits of output precision (default 4 = 0.0001 output)
	-zero PAD 	if provided, output is padded with leading 0s to 
			PAD digits (1.4 with PREC 2 and PAD 3 is "01.400" 
	-scale SCALE	sets scale to 0..SCALE for gini and lorenz data
			(default = 1, i.e. "traditional" gini coefficient)
	-nogini		don't output gini coefficient
	-lorenz		output lorenz data: as many values as input data set
	-ntiles NTILES	output ntiles - e.g. -ntiles 4 outputs quartiles
			(always NTILES data values; rounding errors possible)
	-nan ACTION	if an input line is empty or starts with a non-numeric
			value, ACTION (default: message) is performed - one of:
			exit - prints message to output and exits
			eof - exits without message as if at the end of file
			skip - ignores that line
			msg - prints a message line "NAN ..." to the output
	-id		the first field (need not be numeric) of each line is
			treated as the ID for the dataset on that line, and is
			reproduced unchanged as the first field in the output.
	-comment OPT	by default, lines starting ### in the input are 
			ignored completely. other action is based on OPT:
			skip - default
			none - comments turned off: ### lines treated as data
			copy - lines starting ### are copied as is to output.
	-zeromsg	what to do if the sum of data values is 0? this would
			result in a DIV0 error for gini calculation. by default
			the gini value output is 0, and no tiles or lorenz data
			is output at all. with -zeromsg, the gini value output
			is the text string ZEROSUM.
	-count		output the number of input data elements (i.e. 
			excluding ID field if present). note: to deal with
			buggy input data (all zero), if sum = 0, count = 0.
	-sum		output the sum of input data elements. the format of
			count and sum are not affected by -scale and -precision 

EOT

sub sum (@);
sub gformat (@);
sub gf2 ($);
$prec=4; ## 4 digits of precision 
$scale=1.0;
$ntiles=0;
$giniout=1;
$lorenzout=0;

$zdig=0;
$nanexit=0; $nanmsg=1;
$saveID=0;
$comment=1;
$zeromsg=0;
$outputcount=0;
$outputsum=0;

if ($ARGV[0] eq "--help" || $ARGV[0] eq "-help" || $ARGV[0] eq "-?") { 
	print $helptext;
	exit;
}

if ($ARGV[0] eq "-precision") {
	shift;
	if ($ARGV[0]=~/\D/) {
          print "MUST provide numeric argument for -precision PREC. --help for help.\n";
          exit;
	}
	$prec = $ARGV[0];
	shift;
}

if ($ARGV[0] eq "-zero") {
        shift;
        if ($ARGV[0]=~/\D/) {
          print "MUST provide numeric argument for -zero PAD. --help for help.\n";
          exit;
        }
        $zdig = $ARGV[0];
        shift;
}

if ($ARGV[0] eq "-scale") {
        shift;
        if ($ARGV[0]=~/\D/) {
          print "MUST provide numeric argument for -scale SCALE. --help for help.\n";
          exit;
        }
        $scale = $ARGV[0];
        shift;
}

if ($ARGV[0] eq "-nogini") {
        shift;
        $giniout = 0;
}

if ($ARGV[0] eq "-lorenz") {
        shift;
        $lorenz = 1;
}

if ($ARGV[0] eq "-ntiles") {
        shift;
        if ($ARGV[0]=~/\D/) {
          print "MUST provide numeric argument for -ntiles NTILES. --help for help.\n";
          exit;
        }
        $ntiles = $ARGV[0];
        shift;
}
 
if ($ARGV[0] eq "-nan") {
        shift;
        if ($ARGV[0] eq "exit") {
		$nanexit=1; $nanmsg=1;
	} elsif ($ARGV[0] eq "eof") {
		$nanexit=1; $nanmsg=0;
	} elsif ($ARGV[0] eq "skip") {
		$nanexit=0; $nanmsg=0;
	} elsif ($ARGV[0] eq "message" || $ARGV[0] eq "msg") {
		$nanexit=0; $nanmsg=1;
	} else {
          print "MUST provide argument for -nan ACTION. --help for help.\n";
          exit;
        }
        shift;
}

if ($ARGV[0] eq "-id") {
	$saveID=1;
	shift;
}

if ($ARGV[0] eq "-comment") {
        shift;
        if ($ARGV[0] eq "none") {
                $comment=0;
        } elsif ($ARGV[0] eq "copy") {
                $comment=2;
        } else {
          print "MUST provide argument for -comment OPT. --help for help.\n";
          exit;
        }
        shift;
}

if ($ARGV[0] eq "-zeromsg") {
        $zeromsg=1;
        shift;
}

if ($ARGV[0] eq "-count") {
        $outputcount=1;
        shift;
}

if ($ARGV[0] eq "-sum") {
        $outputsum=1;
        shift;
}

if ($ARGV[0] ne "") {
	$ifname=$ARGV[0];
} else {
	$ifname="-"; ## filename for STDIN
}

open(FIN, "< $ifname") ||die ("can't open $ARGV[0]: $!\nuse --help for help.");


$\="\n"; 
$,=",";

loop:
while (<FIN>) {
	if ($comment > 0 && (substr ($_,0,3) eq "###")) {
		if ($comment == 2) { ## -comment copy flag, so print comment 
			chomp; print $_;
		}
		next; ## skip line starting with ### unless -comment none flag  
	}

	chomp;
	@irect= split /,/;
	
	if ($saveID) {
		if ($#irect >=0) {
			$id=shift @irect;
		} else {
			$id="";
		}
	}
	
        if ($#irect < 0 || $irect[0]=~/\D/) {
		if ($nanmsg==1) {
		   if ($saveID && $id ne "") {
			printf ("%s,", $id);
		   }
		   print "NAN, Non numeric value or blank line in input.";
		}
		if ($nanexit==1) {
			exit;
		} else {
			next loop;
		}
	}

	@irec = sort {$a <=> $b} @irect; ## sort numerically in ascending order
	$#orec= -1; $#lorec= -1; $#tiles= -1;

	$num= $#irec + 1;
	$sum= sum @irec; 
	
	if ($sum==0) { ## prevent divide by 0 error on buggy input data
		$num=0; ## 0 sum, == 0 values.
	}

	$qpop=0; $qdata=0; ## reset cumulative pop, data
	$qpopsh=0; $qdatash=0; 
		## reset cumulative sums for population and data share
	$area=0;
	$tilectr=1; $tilesz=($ntiles)?($num/$ntiles):0;
	$tilesum=0; # sum of previous tiles

	for ($i=0; $i<$num; $i++) {
		$qpop += 1; 
		## increment pop by 1 - note, could be optimised by using
	    	## qpop as iterator from 1..$num, but that'd be confusing
		## also, this allows for future weighted pop increments

		$qdata += $irec[$i];
		## cumulative sum of data points

		$qpopsh= $qpop / $num;
		$qdatash= $qdata / $sum;

		## cumulative shares - note $num means pop is unweighted
		## i.e. data points are treated equally
		
		if ($lorenz || $ntiles) { ## lorenz curve data wanted
			push @lorec, $qdatash; 
		}

		if ($ntiles) {
			if (($i+1)/$tilesz >= $tilectr) { # tile boundary
			   $tiles[$tilectr-1]= $qdatash-$tilesum;
			   # this tile is cum. data share minus previous
			   # tile
			   $tilectr++;
			   $tilesum=$qdatash; # cum. sum of saved tiles
			}
		}

		$area+= ($qpopsh - $qdatash); 
		## calculate area under lorenz curve
	}

	if ($ntiles && $tilectr <= $ntiles && $num) { ## if $num 0, skip this 
		# fix rounding errors by filling final ntile
		$tiles[$tilectr-1]= $qdatash-$tilesum;
	}
	
	if ($lorenz) { 
		@orec= gformat @lorec, @tiles;
	} else { # only tiles
		@orec = gformat @tiles;
	}

	if ($outputsum) {
		unshift @orec, $sum;
	}

	if ($outputcount) {
		unshift @orec, $num;
	}
	
	if ($giniout) { 
		if ($num) {
		  $gini= ($area / $num) * 2 ; 
		  ## gini is mean area * 2 (to bring it to 0..1 scale);
		} else { ## no fields, or sum == 0 so num was set to 0
		  $gini= ($zeromsg)?"ZEROSUM":"0"; ## either txt msg or 0
		}
	
		if ($num || ($zeromsg==0)) { ## $gini is a number or 0
			$ogini= gf2 $gini;
		} else {
			$ogini= $gini; ##kludge.
		}

		unshift @orec, $ogini; 
	}

        if ($saveID) {
                unshift @orec, $id;
        }


	print @orec;
}





sub sum (@){ 		## return sum of all arguments
	my $i= $#_ + 1;
	my $tot=0;
	while ($i--) {
		$tot+= $_[$i];
	}
	return $tot;
}

sub gf2 ($) {
        my $maxdig = $zdig+$prec+1;
        if ($zdig) {
           return (sprintf("%0${maxdig}.${prec}f",  $_[0] * $scale));
        } else {
           return (sprintf("%.${prec}f",  $_[0] * $scale));
        }
}
  
sub gformat (@) {
	my $i =0;
	my @ret; $#ret=-1;
	for (;$i<=$#_; $i++) {	
		push @ret, gf2  $_[$i];
	}
	return @ret;
}

