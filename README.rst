==========================================
Automojo XModules Overview
==========================================

The ``automojo-xmodules`` package contains utility modules that extend
standard Python libraries. Each module name begins with ``x`` to avoid
collisions with the Python modules they extend.

Provided Extensions
-------------------

- **xcollections** – Case-insensitive dictionaries and context management helpers for shared automation state.
- **xconvert** – Safe string/bytes conversions and boolean parsing.
- **xdatetime** – Convenience functions for timestamps and formatted time strings.
- **xfspath** – Path expansion helpers that combine common filesystem path operations.
- **xformatting** – Utilities for indenting multi-line text and formatting command results.
- **ximport** – Functions to import modules dynamically by name or from a file.
- **xinspect** – Helpers for introspecting functions and modules at runtime.
- **xlogging** – Components to simplify logging setup, log levels and monitored execution scopes.
- **xmuliprocessing** – Support for capturing stdout/err from child processes using a piped process abstraction.
- **xpython** – Helpers for manipulating the Python search path in running processes.
- **xthreading** – Thread utilities including a worker "Looper" pool and synchronization primitives such as read/write locks.
- **xzipfile** – Helper for creating zip archives of folders.

These modules are located under ``source/packages/automojo/xmodules`` and are used throughout Automation Mojo projects.

=================
Code Organization
=================
* .vscode - Common tasks
* development - This is where the runtime environment scripts are located
* repository-setup - Scripts for homing your repository and machine setup
* userguide - Where you put your user guide
* source/packages - Put your root folder here 'source/packages/(root-module-folder)'
* workspaces - This is where you add VSCode workspaces templates and where workspaces show up when homed.

==========
References
==========

- `User Guide <userguide/userguide.rst>`
- `Coding Standards <userguide/10-00-coding-standards.rst>`
