#!/usr/bin/perl -w
#monitor.cgi
=begin comment

For my Notepad project.

Monitor for administrative use. So I can see the list of current non-blank
pages and possibly other summary information.

=end comment
=cut

use strict;
use CGI;
use HTML::Template;
use DBI;
use Config::IniFiles;
use CGI::Cookie;
use lib "$ENV{'DOCUMENT_ROOT'}/code";
use DBIconnect;
use Auth;

# Constants
my $root = $ENV{'DOCUMENT_ROOT'};
my $TMPL_FILE = "monitor.tmpl";
my $CONFIG_FILE = "$root/protect/dbi_config.ini";
my $CONFIG_SECTION = "Customizer";
my $NAVBAR_FILE = "$root/navbar.d.html";

# Read in navbar HTML
open(my $navbar_fh, "<", $NAVBAR_FILE) or
	warn "Error: Cannot open navbar file $NAVBAR_FILE: $!";
my $navbar = join('', <$navbar_fh>);

# Set up CGI, HTML::Template, and DBI objects 
my $cgi = new CGI;
my $tmpl = HTML::Template->new(filename => $TMPL_FILE);
my $dbh = DBI_connect($CONFIG_FILE, $CONFIG_SECTION);

# Check the format parameter.
my $format = $cgi->url_param('format');
if (!defined($format)) {
	$format = 'html';
}

# If cookie is not authorized, print error and exit
if (! admin_cookie()) {
	print $cgi->header(-type=>'text/plain', -charset=>'utf-8');
	print "Error: You are not yet authorized for this content.\n";
	# Disconnect from database
	$dbh->disconnect();
	exit(0);
}

# Get notes from MySQL
my ($pages) = get_pages($dbh);

# Set CGI template variables
$tmpl->param( NAVBAR => $navbar );
if (defined(@$pages)) {
	$tmpl->param( PAGES => $pages );
}

# Print the output
if ($format eq 'plain') {
	print $cgi->header(-type=>'text/plain', -charset=>'utf-8');
	for my $page (@$pages) {
		print "$$page{PAGE}\n";
	}
} else {
	print $cgi->header(-type=>'text/html', -charset=>'utf-8');
	print $tmpl->output;
}

# Disconnect from database
$dbh->disconnect();



#################### SUBROUTINES ####################

# Finds all pages with currently existing notes
sub get_pages {
	
	my ($dbh) = @_;
	
	my $query = qq{
		SELECT DISTINCT page
		FROM notepad
		ORDER BY page ;
	};
	
	my $dsh = $dbh->prepare($query);
	$dsh->execute();
	
	my $pages;
	while ( my @row = $dsh->fetchrow_array ) {
		push(@$pages, { PAGE => $row[0] } );
	}
	
	$dsh->finish();
	
	return ($pages);
}
