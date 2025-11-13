<#
.SYNOPSIS
The powershell 'cli.ps1' scipt provides the most-often used commands for this application in a convenient was.

.DESCRIPTION
USAGE
    .\cli.ps1 <command>

COMMANDS
    adminuser           🤖 Create a admin-user via django...
    migrate             📜 Executing database migrations...
    test                🧪 Executing unit-tests...
    runserver           🚀 Starting Django development server...
    compose             🚀 Starting containers with docker compose...
    help, -?            show this help message
#>
param(
  [Parameter(Position=0)]
  [ValidateSet("adminuser", "migrate", "test", "runserver", "compose", "help")]
  [string]$Command
)

function Command-Help { Get-Help $PSCommandPath }

function Command-adminuser {
    Write-Host -ForegroundColor Green "🤖 Create a admin-user via django..."
    uv run python manage.py createsuperuser
}

function Command-migrate {
    Write-Host -ForegroundColor Green "📜 Executing database migrations..."
    uv run python manage.py migrate
}

function Command-test {
    Write-Host -ForegroundColor Green "🧪 Executing tests..."
    uv run python manage.py test -v 2
}

function Command-runserver {
    Write-Host -ForegroundColor Green "🚀 Starting Django webserver..."
    uv run python manage.py runserver
}

function Command-compose {
    Write-Host -ForegroundColor Green "🚀 Prepare static files for serving..."
    If (Test-Path ./static_dir) { Remove-Item -force -recurse ./static_dir }
    
    python manage.py collectstatic -c

    Write-Host -ForegroundColor Green "🚀 Starting containers with docker compose..."
    docker compose -f ./containers/compose.yaml down && docker compose -f ./containers/compose.yaml up --build 
}


if (!$Command) {
    Command-Help
    exit
}

switch ($Command) {
    "adminuser" { Command-adminuser }
    "migrate" { Command-migrate }
    "test" { Command-test }
    "runserver" { Command-runserver }
    "compose" { Command-compose }
    "help"  { Command-Help }
}