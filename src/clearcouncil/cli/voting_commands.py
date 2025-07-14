"""Enhanced CLI commands for voting analysis with integrated processing."""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Optional

from ..analysis.voting_analyzer import VotingAnalyzer
from ..analysis.batch_processor import BatchVotingProcessor
from ..visualization.voting_charts import VotingChartGenerator
from ..glossary.municipal_glossary import MunicipalGlossary
from ..glossary.tooltip_generator import TooltipGenerator
from ..config.settings import CouncilConfig, load_council_config
from ..core.exceptions import ClearCouncilError


def add_voting_analysis_commands(subparsers):
    """Add voting analysis commands to the CLI."""
    
    # Main voting analysis command
    voting_parser = subparsers.add_parser(
        "analyze-voting", 
        help="Analyze representative voting patterns"
    )
    voting_parser.add_argument("council", help="Council identifier")
    voting_parser.add_argument(
        "representative", 
        help="Representative name or district (e.g., 'District 2', 'John Smith')"
    )
    voting_parser.add_argument(
        "time_range", 
        help="Time period (e.g., 'last year', 'last 6 months', '2023-01-01 to 2023-12-31')"
    )
    voting_parser.add_argument(
        "--compare-with", 
        nargs="+", 
        help="Other representatives to compare with"
    )
    voting_parser.add_argument(
        "--download-missing", 
        action="store_true", 
        help="Download missing documents for the time period"
    )
    voting_parser.add_argument(
        "--create-charts", 
        action="store_true", 
        help="Generate visualization charts"
    )
    voting_parser.add_argument(
        "--output-format", 
        choices=["json", "csv", "html", "plain"], 
        default="plain",
        help="Output format for the analysis"
    )
    voting_parser.set_defaults(func=analyze_voting_command)
    
    # District analysis command
    district_parser = subparsers.add_parser(
        "analyze-district", 
        help="Analyze all representatives in a district"
    )
    district_parser.add_argument("council", help="Council identifier")
    district_parser.add_argument("district", help="District identifier (e.g., 'District 2')")
    district_parser.add_argument(
        "time_range", 
        help="Time period (e.g., 'last year', 'last 6 months')"
    )
    district_parser.add_argument(
        "--download-missing", 
        action="store_true", 
        help="Download missing documents for the time period"
    )
    district_parser.add_argument(
        "--create-charts", 
        action="store_true", 
        help="Generate visualization charts"
    )
    district_parser.set_defaults(func=analyze_district_command)
    
    # Batch update command for missing documents
    update_parser = subparsers.add_parser(
        "update-documents", 
        help="Download and process missing documents for a time period"
    )
    update_parser.add_argument("council", help="Council identifier")
    update_parser.add_argument(
        "time_range", 
        help="Time period to ensure coverage for"
    )
    update_parser.add_argument(
        "--force-download", 
        action="store_true", 
        help="Download even if documents appear to exist"
    )
    update_parser.set_defaults(func=update_documents_command)
    
    # Glossary command
    glossary_parser = subparsers.add_parser(
        "explain-terms", 
        help="Get explanations for municipal government terms"
    )
    glossary_parser.add_argument(
        "terms", 
        nargs="+", 
        help="Terms to explain (or 'all' for all categories)"
    )
    glossary_parser.add_argument(
        "--category", 
        help="Show all terms in a specific category"
    )
    glossary_parser.add_argument(
        "--format", 
        choices=["plain", "html", "markdown"], 
        default="plain",
        help="Output format"
    )
    glossary_parser.set_defaults(func=explain_terms_command)


async def analyze_voting_command(args):
    """Execute voting analysis for a representative."""
    try:
        config = load_council_config(args.council)
        
        # Initialize components
        batch_processor = BatchVotingProcessor(config)
        analyzer = VotingAnalyzer(config)
        glossary = MunicipalGlossary()
        tooltip_generator = TooltipGenerator(glossary)
        
        print(f"🔍 Analyzing voting patterns for {args.representative}")
        print(f"📅 Time period: {args.time_range}")
        print(f"🏛️  Council: {config.name}")
        
        if args.download_missing:
            print("📥 Checking for missing documents...")
        
        # Get voting data (with automatic download if requested)
        tracker, metadata = await batch_processor.get_voting_data_for_period(
            args.time_range,
            download_missing=args.download_missing,
            representative_filter=args.representative
        )
        
        print(f"📊 Processing complete:")
        print(f"   • Documents processed: {metadata.get('total_documents_processed', metadata.get('documents_processed', 0))}")
        print(f"   • Representatives found: {metadata.get('representatives_found', 0)}")
        print(f"   • Total votes extracted: {metadata.get('total_votes_extracted', metadata.get('votes_extracted', 0))}")
        
        # Check if we have enough data to proceed
        if metadata.get('total_documents_processed', metadata.get('documents_processed', 0)) == 0:
            print(f"\n⚠️  No documents found for the specified time period!")
            print(f"   This could mean:")
            print(f"   • No documents exist for '{args.time_range}'")
            print(f"   • Documents need to be downloaded (try --download-missing)")
            print(f"   • The council identifier '{args.council}' might be incorrect")
            print(f"\n💡 Try:")
            print(f"   • List available councils: python clearcouncil.py list-councils")
            print(f"   • Download documents: python clearcouncil.py download-pdfs {args.council}")
            print(f"   • Check data directory: {config.get_data_path('pdf')}")
            return
        
        # Perform analysis
        analysis = analyzer.analyze_representative_voting(
            args.representative,
            args.time_range,
            comparison_reps=args.compare_with
        )
        
        # Output results
        if args.output_format == "json":
            import json
            print(json.dumps(analysis, indent=2, default=str))
        elif args.output_format == "csv":
            _output_csv_analysis(analysis, config)
        elif args.output_format == "html":
            _output_html_analysis(analysis, tooltip_generator, config)
        else:
            _output_plain_analysis(analysis, tooltip_generator)
        
        # Generate charts if requested
        if args.create_charts:
            chart_generator = VotingChartGenerator(config)
            
            print(f"\n📈 Generating visualization charts...")
            
            # Representative summary chart
            summary_chart = chart_generator.create_representative_summary_chart(analysis)
            print(f"   • Summary chart: {summary_chart}")
            
            # Comparison chart if we have comparison data
            if 'comparison' in analysis and analysis['comparison']['compared_with']:
                comparison_chart = chart_generator.create_comparison_chart(analysis)
                print(f"   • Comparison chart: {comparison_chart}")
            
            # Timeline chart if we have detailed votes
            if analysis['detailed_votes']:
                timeline_chart = chart_generator.create_timeline_chart(analysis['detailed_votes'])
                print(f"   • Timeline chart: {timeline_chart}")
        
    except ClearCouncilError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


async def analyze_district_command(args):
    """Execute district analysis."""
    try:
        config = load_council_config(args.council)
        
        batch_processor = BatchVotingProcessor(config)
        analyzer = VotingAnalyzer(config)
        
        print(f"🏘️  Analyzing {args.district} representatives")
        print(f"📅 Time period: {args.time_range}")
        
        # Get voting data
        tracker, metadata = await batch_processor.get_voting_data_for_period(
            args.time_range,
            download_missing=args.download_missing
        )
        
        # Perform district analysis
        district_analysis = analyzer.get_district_analysis(args.district, args.time_range)
        
        # Output results
        _output_district_analysis(district_analysis)
        
        # Generate charts if requested
        if args.create_charts:
            chart_generator = VotingChartGenerator(config)
            district_chart = chart_generator.create_district_overview_chart(district_analysis)
            print(f"📈 District overview chart: {district_chart}")
            
    except ClearCouncilError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


async def update_documents_command(args):
    """Update documents for a time period."""
    try:
        config = load_council_config(args.council)
        batch_processor = BatchVotingProcessor(config)
        
        print(f"📥 Updating documents for {args.time_range}")
        
        # Get missing documents info
        analyzer = VotingAnalyzer(config)
        missing_info = analyzer.find_missing_documents(args.time_range)
        
        print(f"📋 Current document status:")
        print(f"   • Existing documents: {missing_info['existing_documents']}")
        print(f"   • Documents in range: {missing_info['documents_in_range']}")
        print(f"   • Recommendation: {missing_info['recommendation']}")
        
        # Download missing documents
        tracker, metadata = await batch_processor.get_voting_data_for_period(
            args.time_range,
            download_missing=True
        )
        
        print(f"✅ Update complete:")
        print(f"   • New documents downloaded: {metadata['downloaded_documents']}")
        print(f"   • Total documents processed: {metadata['total_documents_processed']}")
        
    except ClearCouncilError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def explain_terms_command(args):
    """Explain municipal government terms."""
    glossary = MunicipalGlossary()
    
    if args.category:
        # Show all terms in a category
        terms_in_category = glossary.get_terms_by_category(args.category)
        
        if not terms_in_category:
            print(f"❌ No terms found in category '{args.category}'")
            print(f"Available categories: {', '.join(glossary.get_all_categories())}")
            return
        
        print(f"📚 Terms in category: {args.category.title()}")
        print("=" * 50)
        
        for term, data in terms_in_category.items():
            print(f"\n{term.upper()}")
            print(f"Definition: {data['definition']}")
            if 'explanation' in data:
                print(f"Explanation: {data['explanation']}")
            if 'example' in data:
                print(f"Example: {data['example']}")
    
    elif "all" in args.terms:
        # Show all categories
        categories = glossary.get_all_categories()
        print("📚 Available term categories:")
        for category in categories:
            terms_in_cat = glossary.get_terms_by_category(category)
            print(f"\n{category.upper()} ({len(terms_in_cat)} terms)")
            for term in list(terms_in_cat.keys())[:3]:  # Show first 3 terms
                print(f"  • {term}")
            if len(terms_in_cat) > 3:
                print(f"  • ... and {len(terms_in_cat) - 3} more")
        
        print(f"\nUse --category <name> to see all terms in a category")
    
    else:
        # Explain specific terms
        for term in args.terms:
            term_data = glossary.get_definition(term)
            
            if term_data:
                print(f"\n📖 {term.upper()}")
                print(f"Definition: {term_data['definition']}")
                if 'explanation' in term_data:
                    print(f"Explanation: {term_data['explanation']}")
                if 'example' in term_data:
                    print(f"Example: {term_data['example']}")
                if 'category' in term_data:
                    print(f"Category: {term_data['category']}")
            else:
                print(f"❌ Term '{term}' not found in glossary")


def _output_plain_analysis(analysis: dict, tooltip_generator: TooltipGenerator):
    """Output analysis in plain text format with term explanations."""
    rep = analysis['representative']
    time_period = analysis['time_period']
    
    print(f"\n📊 VOTING ANALYSIS REPORT")
    print("=" * 50)
    print(f"Representative: {rep['name']} ({rep['district']})")
    print(f"Time Period: {time_period['formatted_range']}")
    print(f"Total Votes: {rep['total_votes_in_period']}")
    print(f"Motions Made: {rep['motions_made']}")
    print(f"Seconds Given: {rep['seconds_given']}")
    
    # Voting breakdown
    breakdown = analysis['voting_breakdown']
    print(f"\n📋 Voting Activity Breakdown:")
    print(f"   • Motions Made: {breakdown['motions_made']}")
    print(f"   • Seconds Given: {breakdown['seconds_given']}")
    print(f"   • Votes For: {breakdown['votes_for']}")
    print(f"   • Votes Against: {breakdown['votes_against']}")
    print(f"   • Abstentions: {breakdown['abstentions']}")
    
    # Case categories
    categories = analysis['case_categories']
    if categories:
        print(f"\n🏛️  Cases by Type:")
        for category, count in categories.items():
            print(f"   • {category.title()}: {count}")
    
    # Comparison data
    if 'comparison' in analysis and analysis['comparison']['compared_with']:
        print(f"\n📊 Comparison with Other Representatives:")
        for comp_rep in analysis['comparison']['compared_with']:
            print(f"   • {comp_rep['name']} ({comp_rep['district']}): {comp_rep['votes_in_period']} votes")
    
    # Recent votes
    recent_votes = analysis['detailed_votes'][:10]  # Show last 10
    if recent_votes:
        print(f"\n📝 Recent Voting Activity:")
        for vote in recent_votes:
            print(f"   • {vote['date']}: {vote['formatted_type']} - {vote['case_number']}")
    
    # Add term explanations
    report_text = str(analysis)
    found_terms = tooltip_generator.glossary.find_terms_in_text(report_text)
    
    if found_terms:
        print(f"\n📚 Municipal Terms Used in This Report:")
        print("-" * 40)
        for term in found_terms[:5]:  # Show top 5 terms
            term_data = tooltip_generator.glossary.get_definition(term)
            if term_data:
                print(f"{term.title()}: {term_data['definition']}")


def _output_district_analysis(analysis: dict):
    """Output district analysis in plain text."""
    print(f"\n🏘️  DISTRICT ANALYSIS REPORT")
    print("=" * 50)
    print(f"District: {analysis['district']}")
    print(f"Time Period: {analysis['time_period']}")
    print(f"Total Representatives: {analysis['district_summary']['total_representatives']}")
    print(f"Total Votes: {analysis['district_summary']['total_votes']}")
    print(f"Most Active: {analysis['district_summary']['most_active']}")
    
    print(f"\n👥 Representatives:")
    for rep in analysis['representatives']:
        print(f"   • {rep['name']}")
        print(f"     - Votes in period: {rep['votes_in_period']}")
        print(f"     - Motions made: {rep['motions_made']}")
        print(f"     - Seconds given: {rep['seconds_given']}")


def _output_csv_analysis(analysis: dict, config: CouncilConfig):
    """Output analysis data as CSV files."""
    results_dir = config.get_data_path("results")
    results_dir.mkdir(exist_ok=True)
    
    import pandas as pd
    
    # Main analysis data
    rep_data = {
        'representative': [analysis['representative']['name']],
        'district': [analysis['representative']['district']],
        'total_votes': [analysis['representative']['total_votes_in_period']],
        'motions_made': [analysis['representative']['motions_made']],
        'seconds_given': [analysis['representative']['seconds_given']],
        'time_period': [analysis['time_period']['formatted_range']]
    }
    
    df = pd.DataFrame(rep_data)
    csv_path = results_dir / f"voting_analysis_{analysis['representative']['name'].replace(' ', '_')}.csv"
    df.to_csv(csv_path, index=False)
    print(f"📄 Analysis saved to: {csv_path}")
    
    # Detailed votes
    if analysis['detailed_votes']:
        votes_df = pd.DataFrame(analysis['detailed_votes'])
        votes_csv = results_dir / f"detailed_votes_{analysis['representative']['name'].replace(' ', '_')}.csv"
        votes_df.to_csv(votes_csv, index=False)
        print(f"📄 Detailed votes saved to: {votes_csv}")


def _output_html_analysis(analysis: dict, tooltip_generator: TooltipGenerator, config: CouncilConfig):
    """Output analysis as HTML with interactive tooltips."""
    results_dir = config.get_data_path("results")
    results_dir.mkdir(exist_ok=True)
    
    # Generate HTML report with tooltips
    html_content = _generate_html_report(analysis, tooltip_generator)
    
    html_path = results_dir / f"voting_analysis_{analysis['representative']['name'].replace(' ', '_')}.html"
    with open(html_path, 'w') as f:
        f.write(html_content)
    
    print(f"🌐 Interactive HTML report saved to: {html_path}")


def _generate_html_report(analysis: dict, tooltip_generator: TooltipGenerator) -> str:
    """Generate HTML report with tooltips."""
    rep = analysis['representative']
    
    # Create base report text
    report_text = f"""
    <h1>Voting Analysis Report</h1>
    <h2>{rep['name']} ({rep['district']})</h2>
    
    <p>This representative made {rep['motions_made']} motions and gave {rep['seconds_given']} seconds 
    during the analyzed period. The movant is the council member who proposes actions, while 
    the second supports the motion for discussion.</p>
    
    <p>In total, this representative participated in {rep['total_votes_in_period']} voting activities,
    including rezoning decisions and ordinance votes.</p>
    """
    
    # Add tooltips to municipal terms
    annotated_text = tooltip_generator.annotate_text_with_tooltips(report_text, "html")
    
    # Create glossary sidebar
    sidebar = tooltip_generator.create_glossary_sidebar(report_text, "html")
    
    # Complete HTML document
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Voting Analysis - {rep['name']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .container {{ display: flex; gap: 20px; }}
            .main-content {{ flex: 2; }}
            .sidebar {{ flex: 1; }}
            .municipal-term {{ border-bottom: 1px dotted #007bff; cursor: help; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="main-content">
                {annotated_text}
            </div>
            <div class="sidebar">
                {sidebar}
            </div>
        </div>
    </body>
    </html>
    """
    
    return html