# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),

## -- 2021-03-30

### Added
- Functions to create Sample Types when creating a Field Type
- Functions to create Object Types when creating a Field Type
- Command Line flag to override conflict checks and overwrite instance data with local data

### Changed
- Added more detail to definition files for Sample Types and Field Types


## -- 2021-02-24 -- [1.1.0] 

### Added
-- Functions to create Field Types based on Definition Files


## -- 2021-02-02

### Changed
- Push operation type, if called from test function, now only pushes protocol and test files.
- When running tests, a seperate file is created containing the backtrace


## [1.0.0] – 2020-12-23

### Added

- Function to create libraries
- Functions to pull data about sample and object types when pulling operation types 
- Ability to run ruby code tests for operation types
- When pulling operation types, a test file will be created if one doesn't already exist
- Ability to push an entire category/directory
- Functions to show configurations and notify user which configuration they are currently using
- This changelog 
- Pushing operation types or libraries that don't already exist will cause them to be created

### Changed

- pydent version updated to 1.04
- Base Docker Image updated to python 3.9
- Boilerplate code now added to new code objects when creating Operation Types or Libraries

### Fixed

- Fix typos in recent README changes.

### Removed


## [0.0.2] - 2020-12-15

## [0.0.1] - 2020-06-20


