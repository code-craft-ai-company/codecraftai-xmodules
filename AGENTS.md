# Personality
AI Agents working in this repository should refer to themselves as an agent named 'CodeCraftX'.

# Rules
- Look in the '<repository>/specs' folder for specification files that help to steer development work
- Look in the '<repository>/userguide' folder for files containing standards and conventions
- Look in the '<repository>/prompts' folder for pre-build prompts
- Files inside the .venv folder should not be modified, they are modified by the setup scripts
- Use the '<repository>/source/examples' folder for example, debug and test scripts

# Project Overview
The 'codecraftai-xmodules' package is a repository that provides extended functionality for base python modules.  The xmodules are all named
with a preceding 'x' so as not to create module name conflicts with the python modules they target to extend functionality.

# Description
The codecraftai-xmodules package is organized under `source/packages/ccai/xmodules/` and provides the following modules and sub-packages:

## Core Utility Modules
*  **constants.py** - Package-wide constants such as the URL separator character.
*  **debugging.py** - Debugging utilities including multi-debugger support (PDB, DebugPy), VSCode debugger detection, well-known conditional breakpoints, and the `DebugPyAssistant` class for remote debugging via a daemon thread endpoint.
*  **fspath.py** - File system path manipulation covering path expansion, Python module collection from directory trees with depth limiting, package directory creation with automatic `__init__.py` generation, module/package path resolution, and path normalization.
*  **jsos.py** - JSON Stream Object (JSOS) file format support for loading record-separated (0x1E) JSON data streams into lists of dictionaries.
*  **xconvert.py** - Type conversion utilities for boolean parsing from common string representations, safe str/bytes conversion with UTF-8 encoding, and separated list parsing with normalization.
*  **xdatetime.py** - Extended datetime functionality providing millisecond timestamps, fractional time formatting with microsecond precision, custom format constants, and datetime parsing.
*  **xformatting.py** - Text formatting utilities for command result output, configurable multi-level line indentation, and whitespace normalization.
*  **ximport.py** - Dynamic module importing by fully qualified name or by file path, with proper sys.modules caching.
*  **xinspect.py** - Code inspection utilities for retrieving current and caller function names from the call stack, module ancestry analysis, and type checking.
*  **xpython.py** - Python environment manipulation for prepending/appending to `sys.path` and synchronizing the `PYTHONPATH` environment variable for child processes.
*  **xvariables.py** - Application variable management system using Python descriptors. Provides `VariableDesc` for declaring variables with section, default, source (environment, settings, or both), and optional converters. Includes `VariableReader` for descriptor-based access and `VariableSet` as a base class for variable declaration groups. Validates variable and section names against environment variable naming rules.
*  **xzipfile.py** - Archive creation utility for compressing folders into ZIP files with configurable compression levels and automatic directory structure preservation.

## eventing/ Sub-Package
An event-driven state variable system for tracking and propagating values from remote objects.
*  **enumerations.py** - Defines `EventedVariableState` (UnInitialized, Default, Valid, Stale).
*  **eventedvariable.py** - `EventedVariable` class for thread-safe storage and propagation of event values with subscription expiration, wait-for-update/value operations with configurable timeouts, and weak reference management to the owning sink.
*  **eventedvariablesink.py** - `EventedVariableSink` class acting as a container for evented variables. Manages subscription lifecycle, auto-subscription, initiator moment tracking, and provides a generator-based state lock yielding pattern. Requires subclasses to implement `invalidate_subscription`, `renew_subscription`, and `trigger_auto_subscribe_from_variable`.

## xcollections/ Sub-Package
Enhanced collection types and dictionary utilities.
*  **caseinsensitivebytesdict.py** - `CaseInsensitiveBytesDict`, a dict subclass providing case-insensitive lookups for bytes keys by normalizing keys to lowercase.
*  **caseinsensitivestringdict.py** - `CaseInsensitiveStringDict`, a dict subclass providing case-insensitive lookups for string keys by normalizing keys to lowercase.
*  **dictmap.py** - `DictMap` class providing a file-system-like path interface (e.g. `/a/b/c`) for navigating, inserting, looking up, and removing values in nested dictionaries.
*  **helpers.py** - Utility function `insert_into_ordered_list_ascending` for inserting items into a pre-sorted list while maintaining ascending order.
*  **mergemap.py** - `MergeMap`, a `MutableMapping` implementation similar to `ChainMap` but with type-aware merging that recursively combines dict values into nested MergeMaps and deduplicates list/tuple values across maps.
*  **wellknown.py** - Thread-safe singleton factory `ContextSingleton()` for a global `Context` instance. Note: references a `context.py` module that is not yet present in the repository.

## xlogging/ Sub-Package
Advanced logging capabilities with multiple activation modes.
*  **activation.py** - Logging activation functions for three modes: service (rotational logs), interactive (no stdout interference), and command-line (dual console/file output). Tracks activation per process ID and supports remote process logging with unique identifiers.
*  **enhancedloggers.py** - `EnhancedLogger` wrapper around `logging.Logger` adding `render()` for dual console/log output, `section()` for formatted section headers, and `test_begin()`/`test_end()` for test lifecycle logging.
*  **initializations.py** - Referenced by activation.py for `reinitialize_logging_as_service`, `reinitialize_logging_as_interactive`, and `reinitialize_logging_to_standard_file` functions.
*  **levels.py** - `LogLevel` IntEnum extending standard logging levels with a QUIET level (1000).
*  **logginghelpers.py** - Logging helper utilities.
*  **monitoredscope.py** - Monitored scope utilities.
*  **parameters.py** - `LoggingLocation` (directory, basename, ext) and `LoggingReduction` configuration classes.
*  **recordfilters.py** - Log record filtering utilities.
*  **scopemonitor.py** - Scope monitoring utilities.
*  **swappablehooks.py** - `SWAPPABLE_HOOKS` class holding references to `sys.stdout` and `sys.stderr` that can be swapped for testing purposes.

## xthreading/ Sub-Package
Threading and concurrency utilities.
*  **lockscopes.py** - `LockedScope` and `UnLockedScope` context managers for exception-safe lock acquisition and temporary lock release, with convenience factory functions.
*  **looper.py** - `Looper` base class for worker threads that process items from a `LooperQueue`. Provides start/wait lifecycle, a start gate for synchronization, and an abstract `loop(packet)` method for subclasses to implement.
*  **looperpool.py** - `LooperPool` thread pool that dynamically scales worker `Looper` threads between configurable min/max counts based on a high-water mark queue depth. Supports graceful shutdown via `LooperQueueShutdown` sentinel objects.
*  **looperqueue.py** - `LooperQueue` providing a thread-safe work queue backed by a list, RLock, and Semaphore. Supports single and bulk push operations, blocking pop, and coordinated shutdown.
*  **readwritelock.py** - `ReadWriteLock` allowing multiple concurrent readers or a single writer with timeout support, writer starvation prevention via a read gate, and semantic error reporting for misuse.

## xmuliprocessing/ Sub-Package
Multiprocessing enhancements for output capture.
*  **pipedprocess.py** - `PipedProcess`, a `multiprocessing.Process` subclass that redirects child process stdout/stderr through multiprocessing Queues and monitors them via background threads in the parent process.
*  **remotestdtee.py** - `RemoteStdTee`, a `StringIO` subclass that tees write output to both the original file handle and a multiprocessing Queue, with PID-tagged line-buffered forwarding.

# Testing Conventions
The 'codecraftai-xmodules' package repository utilizes the 'unittest' framework in order to test the functionality of the code.

## Test Granularity
Tests should verify the functionality of individual components or functions in isolation, focusing on a single aspect of the code for clarity and maintainability.

Avoid composite tests that validate multiple components or functions in a series of assertions, as they lack proper isolation and can miss checks when an assertion fails.

Use Python's `unittest` framework with `setUp` and `tearDown` methods to establish shared conditions across tests while maintaining separation of concerns.

# Code Naming Conventions
The code naming conventions of this repository follows the [Code Craft AI Python Naming Conventions](userguide/10-02-naming-conventions.rst)


# Code Structure
The code structure of this repository follows the [Code Craft AI Python Code Structure Standards](userguide/10-01-code-organization.rst)


# Coding Standards
The code in this repository is meant to be utilized by testing tools and test frameworks.  Therefore, the code must prioritize:

*  debuggability over performance
*  readability over conciseness

For all the code in this repository, follow the coding standards specified at [Coding Standards](userguide/10-00-coding-standards.rst)


# Environment Setup

## Codex Container Setup
When work is being done on this repository using the Codex web environment.  Use the script 'development/setup-agent-container' as the setup script for Codex containers.

## Development Environments
When checking out the code for this repository in order to test changes, agents must:

* run the 'repository-setup/rehome-repository' script.  It creates a needed '.env' file.
* run the 'development/setup-envrionment' script in order to create the virtual environment.

# Project Specific Rules


## Organization of UnitTest Tests
All the tests for this package are organized under 'source/tests/ccai_tests/xmodules' utilizing a tree structure corresponding to the module file the tests
target.  For example:

   The tests for 'source/packages/ccai/xmodules/xthreading/looper.py' should be located in a file 'source/tests/ccai_tests/xmodules/xthreading/test_looper.py'


# Running Tests
In order to run the unittest tests, you must first enter the virtual environment by running the command:

```
    source <repository-root>/.venv/bin/activate
```

When you setup the environment, the '.venv/bin/activate' script is modified so that it will pull in the appropriate environment
variables from the '.env' file.

For running the 'unittest' tests located under the folder '<repository-root>/source/tests', use the command:

```
    cd <repository-root>

    .venv/bin/python-env -m unittest discover -s source/tests -p "test_*.py"
```


# Pull Request Guidelines


# Packaging
Currently, this package is utilized using a reference to the github repository.  It is currently not published.


# Running Code
This repository utilizes a virtual environment wrapper script to correctly set up the `PYTHONPATH` from the `.env` file and execute Python code.

- **Linux / macOS:** Use `.venv/bin/python-env <script.py>`
- **Windows:** Use `.venv/bin/python-env.ps1 <script.py>`

Do not activate the virtual environment manually or use the global Python interpreter. Always execute scripts through the `python-env` wrapper to ensure the repository code and dependencies are properly linked.
