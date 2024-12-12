# EconomySimulator
This system simulates a planned economy, modeling the flow of resources in detail and integrating multiple production stages. It utilizes data on industries, products, inputs, labor, and population demands to create complex and realistic economic scenarios. The goal is to provide a platform capable of reproducing the functioning of production and consumption in different sectors, making it ideal for strategy games or industrial production analysis in studies and estimations.

The system is powered by tables representing the stages of the production process, such as Extraction, Refining, and Processing. These tables contain information about products, industries, inputs, demands (both direct and popular), and the resources required for each stage. Based on this data, the code simulates interactions between industries, stock management, and demand fulfillment, enabling the exploration of challenges and bottlenecks in a detailed economic model.

-----------------------------

1. Table Data - 
Product: Name of the product to be produced at this stage.
Industry: Name of the industry responsible for producing the product at this stage.
Difficulty: A value reflecting the effort required to produce the product.
Labor: The amount of labor allocated to the product's production.
Demand: Direct demand for the product (may be null if the product is used only as input for another stage).
Popular_Demand: Popular demand for the product, proportional to the population.
Availability: Initial quantity of the product available, if applicable.
Input1, Qty1: Name of the first input needed to produce the product and the required quantity per unit of product.
Input2, Qty2: Name of the second input needed and its quantity.
Material1, Qty1, Material2, Qty2, ..., MaterialN, QtyN: Name and quantity of additional raw materials used as inputs to produce the product.
2. Classes - 
Product: Represents a product with attributes like production difficulty, initial availability, and allocated labor.
Industry: Represents an industry with productivity and a list of products it can manufacture. Contains a method to calculate production quantities and update the stock.
Stock: Stores and manages the available quantities of products and inputs. Provides methods to add, consume, and check item availability.
3. Auxiliary Functions - 
initialize_multistage_industries: Creates industries and associates products with them based on the provided tables and productivity data.
calculate_demand and calculate_demand_i: Calculate the cumulative demand for each product, considering direct demands, popular demands (proportional to the population), and the inputs needed for production in subsequent stages.
process_stage: Simulates production for a specific stage. Evaluates if resources in the stock are sufficient and records products that could not be produced due to input shortages.
calculate_minimum_productivity: Determines the minimum productivity required to meet the demand for each product.
process_industries: Consolidates information about industries, including the products they produce, inputs they use, and the productivity needed.
4. Main Function (main) - 
Reads tables representing different stages of the production process from a .ods file.
Calculates the cumulative demand and the minimum productivity required for each product.
Processes industry information and saves the data to a new file.
Initializes industries and products based on the tables.
Simulates production for each stage:
In extraction stages, products are directly created.
In other stages, it considers input availability and records products that could not be produced.
Displays the final stock and lists products that were not produced due to input shortages.

----------------

# Production Logic Description

1. Industries and Production Chains: 
Each industry represents an economic sector, from resource extraction to the manufacturing of final consumer goods.
Industries are characterized by productivity, determining their efficiency in converting labor and inputs into products.
Industries have lists of products they can manufacture, with varying difficulty and associated demand.
2. Products and Production Stages: 
Products are defined by their production difficulty, popular demand, required labor, and necessary inputs.
3. Popular Demand and Natural Resources: 
The demand for final products, such as food, medicine, clothing, and technological devices, is partially based on population data adjusted to reflect consumption patterns and partially defined arbitrarily.
Natural resources have an initially limited availability, constraining extraction capacity in the initial stages of the production chain.
4. Stocks and Resource Flow: 
A centralized stock system controls resource, input, and product levels at each stage.
Stocks are dynamically updated as industries consume inputs and produce new items.

---------------------------

Production Factors Modeling

Difficulty Factor

The "difficulty" attribute reflects the technical, logistical, and technological challenges of producing each item. It directly influences:
The quantity of inputs required.
Labor efficiency.
Overall industry productivity.
Although defined arbitrarily, the difficulty factor is adjusted to maintain consistency with real-world production:
Example 1: Extracting gold is as difficult as extracting silver, but market value and rarity depend on geological availability and subsequent processing.
Example 2: High-tech products, like Enriched Uranium, have significantly higher difficulty due to specialized processes.

Productivity Factor

Productivity is an industry attribute rather than a product attribute, ensuring consistency within a sector. This model simulates:
An industry's ability to manufacture different items with the same basic efficiency.

Demand Modeling

Demand for products is central to the simulation, comprising:
Popular Demand: Reflects direct population consumption, calculated based on:
Food: Estimated from weekly caloric needs for an average human, adjusted above average consumption.
Medicine and Beverages: Based on average national consumption (e.g., Brazilian patterns for alcohol and medicine).
Clothing, Electronics, and Others: Estimated from arbitrary consumption patterns, adjustable as new data becomes available.
Industrial Demand: Represents the inputs needed to sustain the production of intermediate and final goods. This component is automatically calculated based on production chains.
Cumulative demand propagates through production stages, prioritizing basic products to meet subsequent stages' needs.

Input and Raw Material Modeling

Water and Energy are fixed inputs required for producing all products, in varying quantities.
The definition of other inputs and their quantities aims to follow realistic criteria but requires pragmatic adjustments to balance realism and system functionality:
Realistic Proportions: Some inputs are adjusted to reflect real-world ratios and maintain coherence.
Example:
Iron ore: ~50% concentration.
Copper ore: Adjusted to ~6% for normalization.
Steel: Simplified to 50% iron, 50% coke from its real ratio.
Increasing Complexity: As products progress through production stages, they require more specific inputs and raw materials, creating richer interdependence between sectors.
Inputs also influence the stock system, setting production limits and encouraging strategies for resource optimization.

--------------------------------------

Example Production Chain by Stages

Stage 1: Extraction
Industry: Mining
Product: Mineral Aggregates
Inputs: Water, Energy
Stage 2: Refining
Industry: Mineral Processing
Product: Sand
Inputs: Water, Energy, Mineral Aggregates
Stage 3: Processing
Industry: Glassmaking
Product: Glass
Inputs: Water, Energy, Sand, Limestone
Stage 4: Packaging
Industry: Food
Product: Fruit Jar
Inputs: Water, Energy, Glass, Preserved Fruit
Stage 5: Consumer Goods
Industry: Domestic Goods
Product: Kitchenware
Inputs: Water, Energy, Glass, Polymer, Iron-Aluminum Alloy
Stage 6: Heavy Industry
Industry: Construction
Product: House
Inputs: Water, Energy, Glass, Wood, Concrete, Hammer

Ellipses: Variables, factors, attributes
Boxes: Processes
White Node and Black Arrow: Implemented and functional processes
Red Node and Arrow: Non-implemented processes
