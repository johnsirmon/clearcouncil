"""CLI integration for web interface."""

import asyncio
import logging
from pathlib import Path
from typing import Dict, Optional
import click

from ..config.settings import load_council_config, list_available_councils
from .data_processor import DataProcessingManager
from .database import DatabaseManager
from .app import create_app

logger = logging.getLogger(__name__)


@click.group()
def web():
    """Web interface commands."""
    pass


@web.command()
@click.option('--host', default='0.0.0.0', help='Host to bind to')
@click.option('--port', default=5000, help='Port to bind to')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.option('--config', default='development', help='Configuration name')
def serve(host: str, port: int, debug: bool, config: str):
    """Start the web server."""
    app = create_app(config)
    
    click.echo(f"Starting ClearCouncil web server on {host}:{port}")
    click.echo(f"Debug mode: {debug}")
    
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        click.echo("\nShutting down web server...")
    except Exception as e:
        click.echo(f"Error starting web server: {e}")
        raise


@web.command()
@click.argument('council_id')
@click.option('--force', is_flag=True, help='Force reprocessing of all documents')
def process_data(council_id: str, force: bool):
    """Process data for web interface."""
    if council_id not in list_available_councils():
        click.echo(f"Error: Council '{council_id}' not found")
        return
    
    click.echo(f"Processing data for council: {council_id}")
    
    async def run_processing():
        manager = DataProcessingManager(council_id)
        results = await manager.full_processing_pipeline(force_reprocess=force)
        
        if results.get("success"):
            click.echo("✅ Processing completed successfully!")
            
            # Display results
            doc_processing = results.get("document_processing")
            if doc_processing:
                click.echo(f"   📄 Documents: {doc_processing.processed_documents}/{doc_processing.total_documents} processed")
                click.echo(f"   📊 Records: {doc_processing.total_records} voting records extracted")
                click.echo(f"   ⏱️  Time: {doc_processing.processing_time:.2f} seconds")
            
            stats_update = results.get("statistics_update")
            if stats_update:
                click.echo(f"   👥 Representatives: {stats_update.get('updated_representatives', 0)} updated")
            
            index_creation = results.get("index_creation")
            if index_creation:
                click.echo(f"   🔍 Indexes: {index_creation.get('created_indexes', 0)} created")
            
            click.echo(f"   ⚡ Total processing time: {results.get('total_processing_time', 0):.2f} seconds")
            
        else:
            click.echo("❌ Processing failed!")
            click.echo(f"   Error: {results.get('error', 'Unknown error')}")
    
    try:
        asyncio.run(run_processing())
    except KeyboardInterrupt:
        click.echo("\nProcessing interrupted by user")
    except Exception as e:
        click.echo(f"Error during processing: {e}")
        raise


@web.command()
@click.argument('council_id')
def status(council_id: str):
    """Show processing status for a council."""
    if council_id not in list_available_councils():
        click.echo(f"Error: Council '{council_id}' not found")
        return
    
    manager = DataProcessingManager(council_id)
    status_info = manager.get_status()
    
    click.echo(f"Status for council: {council_id}")
    click.echo("=" * 50)
    
    # Document status
    doc_status = status_info.get("document_status", {})
    click.echo(f"📄 Documents:")
    for status, count in doc_status.items():
        click.echo(f"   {status}: {count}")
    
    # Records and representatives
    click.echo(f"📊 Voting Records: {status_info.get('total_voting_records', 0)}")
    click.echo(f"👥 Representatives: {status_info.get('total_representatives', 0)}")
    
    # Date range
    date_range = status_info.get("date_range", {})
    if date_range.get("start") and date_range.get("end"):
        click.echo(f"📅 Date Range: {date_range['start']} to {date_range['end']}")
    
    # Last updated
    click.echo(f"🕐 Last Updated: {status_info.get('last_updated', 'Unknown')}")


@web.command()
def init_db():
    """Initialize the database."""
    click.echo("Initializing database...")
    
    try:
        db = DatabaseManager()
        click.echo("✅ Database initialized successfully!")
        
        # Show table information
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            click.echo(f"📊 Created {len(tables)} tables:")
            for table in tables:
                click.echo(f"   - {table[0]}")
                
    except Exception as e:
        click.echo(f"❌ Error initializing database: {e}")
        raise


@web.command()
@click.argument('council_id')
@click.option('--output', default='status.json', help='Output file path')
def export_status(council_id: str, output: str):
    """Export processing status to JSON file."""
    if council_id not in list_available_councils():
        click.echo(f"Error: Council '{council_id}' not found")
        return
    
    manager = DataProcessingManager(council_id)
    status_info = manager.get_status()
    
    import json
    
    try:
        with open(output, 'w') as f:
            json.dump(status_info, f, indent=2, default=str)
        
        click.echo(f"✅ Status exported to {output}")
        
    except Exception as e:
        click.echo(f"❌ Error exporting status: {e}")
        raise


@web.command()
def list_councils():
    """List available councils."""
    councils = list_available_councils()
    
    click.echo("Available councils:")
    click.echo("=" * 30)
    
    for council_id in councils:
        try:
            config = load_council_config(council_id)
            click.echo(f"📍 {council_id}")
            click.echo(f"   Name: {config.name}")
            click.echo(f"   Description: {config.description}")
            
            # Get quick status
            manager = DataProcessingManager(council_id)
            status_info = manager.get_status()
            
            click.echo(f"   Records: {status_info.get('total_voting_records', 0)}")
            click.echo(f"   Representatives: {status_info.get('total_representatives', 0)}")
            click.echo()
            
        except Exception as e:
            click.echo(f"   Error loading config: {e}")
            click.echo()


@web.command()
@click.argument('council_id')
@click.option('--backup-dir', default='backups', help='Backup directory')
def backup_data(council_id: str, backup_dir: str):
    """Backup council data."""
    if council_id not in list_available_councils():
        click.echo(f"Error: Council '{council_id}' not found")
        return
    
    backup_path = Path(backup_dir)
    backup_path.mkdir(exist_ok=True)
    
    import shutil
    from datetime import datetime
    
    # Create timestamped backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = backup_path / f"{council_id}_backup_{timestamp}.db"
    
    try:
        # Copy database
        db_path = Path('data/clearcouncil.db')  # Default database path
        if db_path.exists():
            shutil.copy2(db_path, backup_file)
            click.echo(f"✅ Database backed up to {backup_file}")
        else:
            click.echo("❌ Database file not found")
            
    except Exception as e:
        click.echo(f"❌ Error creating backup: {e}")
        raise


# Add to existing CLI
def add_web_commands(cli):
    """Add web commands to existing CLI."""
    cli.add_command(web)


if __name__ == '__main__':
    web()