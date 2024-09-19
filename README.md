# Comoputer_Architecture_Project

## Reuse Distance Calculation Project
This project focuses on implementing and comparing methods for reuse distance calculation in cache memory systems. The reuse distance is a metric that measures the number of distinct memory accesses that occur between two accesses to the same memory address. This metric is crucial for analyzing cache behavior and optimizing its performance.

## Overview
Two main methods for calculating reuse distance have been implemented and evaluated in this project:

Stack-Based Method: This method utilizes a stack to store observed memory addresses. On each access, the stack is searched, and push/pop operations are performed. While simple, this method has a time complexity of $O(n^2)$, making it inefficient for large datasets.

Tree-Based Method: This method leverages an optimized tree data structure to calculate the reuse distance with a time complexity of $O(nlogn)$. It is more efficient and better suited for larger datasets compared to the stack-based approach.

## Features
Implementation of two algorithms for reuse distance calculation.
Comprehensive comparison of the two methods, including performance analysis.
The project is designed for further optimization and can be extended for future research in cache memory systems.
Repository Structure
src/: Contains the source code for both methods.
docs/: Documentation and reports related to the project.
tests/: Test cases for validating the algorithms.
## How to Use
To clone and run the project, follow these steps:

```
git clone <repository-url>
cd project-directory
python main.py
```
Authors
Ali Majidi
Artin Barqi
Amirreza Inanloo
Bardia Rezaei Kalantari
Supervisor
Hossein Asadi
