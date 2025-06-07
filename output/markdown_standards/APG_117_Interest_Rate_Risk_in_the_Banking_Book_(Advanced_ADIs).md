Table of contents

* [Document](#detail)
* [Related Documents](#related)

Prudential practice guide

APG 117 Interest Rate Risk in the Banking Book (Advanced ADIs)
==============================================================

* Banking
* Current

  1 January 2008
  –

  30 September 2025

Prudential framework pillars

Financial Resilience

Capital

Supporting

Table of contents

About this guide
----------------

*[Prudential Standard APS 117 Capital Adequacy: Interest](/standard/aps-117)*

*Rate Risk in the Banking Book* ([APS 117](/standard/aps-117)) sets out APRA’s requirements of authorised deposit-taking institutions (ADIs) in relation to the management and measurement of interest rate risk in the banking book (IRRBB) and the holding of regulatory capital against this risk. This prudential practice guide aims to assist ADIs in complying with these requirements and, more generally, to outline prudent practices in relation to the management and measurement of IRRBB.

Subject to the requirements of [APS 117](/standard/aps-117), ADIs have the flexibility to configure their IRRBB management framework in the way most suited to achieving their business objectives.

Disclaimer and copyright

This prudential practice guide is not legal advice and users are encouraged to obtain professional advice about the application of any legislation or prudential standard relevant to their particular circumstances and to exercise their own skill and care in relation to any material contained in this guide.

APRA disclaims any liability for any loss or damage arising out of any use of this prudential practice guide.

This prudential practice guide is copyright. You may use and reproduce this material in an unaltered form only for your personal non-commercial use or noncommercial use within your organisation. Apart from any use permitted under the *Copyright Act 1968*, all other rights are reserved. Requests for other types of use should be directed to APRA.

Repricing and yield curve risks
-------------------------------

### Repricing assumptions

To estimate repricing and yield curve risks, [APS 117](/standard/aps-117) requires an ADI to make repricing assumptions regarding the repricing of items that do not have a contractually defined repricing date or where there is potential for significant variation between contractual and actual repricing dates. An ADI’s repricing assumptions typically include the following:

fixed-rate banking book items could be assumed to reprice according to the residual term to expected principal repayments, while floating-rate items could be assumed to reprice according to the residual term to the next expected repricing date. For the purpose of determining the expected amount and timing of principal payments, the ADI would normally take into account expected customer behaviour, such as prepayments;

banking book items that are large in volume and small in individual amount, such as instalment or mortgage loans, may be given a simplified assumed repricing term based on statistically supported assessment methods;

banking book items with no or low associated interest flows, such as at-call non-interest bearing deposits and low-interest transaction accounts, may be assumed to have a repricing term that is either zero or a longer period that reflects the lack of sensitivity of the customer rate (if any) to wholesale market rates. An ADI would generally be expected to provide analysis to support use of a non-zero term;

futures and forward contracts, including forward rate agreements, may be treated as a combination of long and short positions (e.g. an ADI that has bought a June 90-day bank bill future could report the position, as at April, as a principal outflow at two months and a principal inflow at five months);

interest rate swaps could be treated as two notional positions with relevant tenors (e.g. a fixed-for-floating interest rate swap under which the ADI is paying fixed-rate interest may be treated as a principal outflow at the maturity date of the swap and a principal inflow at the next interest rate reset date); and

options could be treated on the basis of the delta-equivalent amounts of the underlying or the notional underlying. A more sophisticated approach would involve full revaluation at the beginning and end of the holding period.

An ADI’s repricing assumptions broadly portray the expected repricing of its banking book items. Prepayments or interest rate renegotiations for which the ADI charges an economic penalty that approximates the economic cost of altering from the contractual position, could provide a basis for using contractual rather than expected repricing.

### Non-interest income

In modelling repricing and yield curve risks, an ADI’s internal model would generally reflect all material interest rate sensitivities associated with the ADI’s banking book items, including sensitivities arising from both interest income and non-interest income. Examples of items where interest rate sensitivity arises from non-interest income include:

servicing rights and other fee income streams from products (not necessarily issued or owned by the ADI), the volumes of which are correlated with interest rates; and

properties owned by the ADI that have values that are materially affected by interest rates.

### Approaches to modelling interest rate variability

APRA believes it is unnecessarily prescriptive to specify the model used by an ADI to measure its risk. However, [paragraph 29 of APS 117](/standard/aps-117#Item-29) requires an ADI to ensure that its modelling approach meets the soundness standard, so some guidance is appropriate on this point.

The most common approach used by ADIs in Australia for modelling changes in market rates in recent years has been the historical sampling approach. A difficulty encountered under this approach with a one-year holding period is the absence of a data set of independent observations large enough to use for estimating a 99 per cent confidence interval. A larger set of observations from which to draw can be obtained by using changes over overlapping one-year intervals at daily rests, over a period of six years or so. However, this approach introduces a problem that the overlap will cause very heavy correlation between the observations, thereby undermining the statistical validity of the method. It will be more difficult for an ADI to satisfy APRA that an approach using overlapping periods satisfies the soundness standard than an approach that does not suffer from the problem of correlated observations. Some other approaches that could be taken which do not suffer from this problem, or which can mitigate it, are:

modelling interest rate changes over a shorter holding period using non-overlapping observations (by a method of the ADI’s choice, e.g. historical sampling, variance-covariance, Monte Carlo) and scaling up the changes by a suitable factor before applying to the portfolio to get a simulated profit and loss result;

measuring value-at-risk (VaR) over a shorter holding period using non-overlapping observations (again by a method of the ADI’s choice) and scaling up the result by a suitable factor;

using Monte Carlo simulation to generate interest rate changes over successive short periods and chain-linking the changes over these shorter periods to build up the simulated changes over a year;

in combination with using a shorter holding period and scaling up to one year, measuring results for a lower confidence level than 99 per cent and scaling up to 99 per cent using a ratio of percentiles from a suitable reference distribution; and

using antithetic variables (e.g. for each yield curve change in the observation set, also using the opposite change, on an arithmetic or geometric basis as is determined to be appropriate) or other variance reduction techniques, where determined to be appropriate, to maximise the amount of information than can be extracted from the limited data set.

If an ADI uses a chain-linked Monte Carlo approach, consideration could be given to the appropriateness of setting the simulated changes within a ‘term structure model’ framework that imposes certain relationships between rates of different tenor and constrains how rates at a given tenor may change over time. Such approaches may contain elements such as mean reversion and use of implied volatilities observed from market instruments. These approaches typically have more degrees of freedom than historical sampling, providing more flexibility to the user. Although such flexibility can be positive, allowing the user to better tailor the model to reflect the risks, APRA envisages that any approach chosen will be used consistently.

### Earnings offset

When modelling the amount of regulatory capital required by an ADI for repricing and yield curve risks, [APS 117](/standard/aps-117) allows the ADI to include an earnings offset which is an adjustment for the impact of interest rate changes on economic value-based earnings during the holding period. In essence, the adjustment will tend to offset changes in the economic value of the ADI’s banking book.[1]

[1]

For example, an interest rate increase will generally reduce the economic value of the banking book, but economic value-based earnings will be higher for the period from the increase date to the end of the holding period.

As detailed in [APS 117](/standard/aps-117), the earnings offset is the economic value, as at the beginning of the holding period (time *t*), of a notional portfolio of fixed-for-floating interest rate swaps. In calculating the earnings offset of the notional portfolio, APRA would generally envisage the following assumptions to be applied:

the ADI receives fixed-rate payments;

the maturity dates of the interest rate swaps are at monthly intervals from one to

12 months after time *t;*

the inception dates for the swaps maturing *m* months after time *t* are at monthly intervals from time *t* back to (12 - *m*) months before time *t* (i.e. there are 78 swaps in the notional portfolio);

the fixed rate for each interest rate swap is the rate that would have applied at its inception given its original maturity; and

the principal amount of each swap incepted at *k* months before time *t* and maturing *m* months after *t* is 1/12 times;

if *k* + *m*=12 (i.e. the swap has an original maturity of 12 months), the book value of the banking book at the swap’s inception date, or

the increase in the book value of the banking book over the month immediately preceding the swap’s inception date.

Variations from the above assumptions by an ADI may be considered by APRA on a case-by-case basis.

The moving average of the notional portfolio of interest rate swaps extends out to 12 months in order to match the length of the holding period required by the soundness standard detailed in [APS 117](/standard/aps-117). The impact of the earnings offset on the ADI’s IRRBB capital requirement will be approximate to the economic-value-based earnings offset that arises during the 12-month holding period from interest rate changes, assuming that the ADI maintains a stable repricing profile for its banking book throughout that period. The effect of including the earnings offset is mechanically equivalent to assuming an investment term of capital of 12 months; however, the reasoning for the earnings offset’s inclusion may not be the same as ADIs use when deciding their investment term of capital for internal management of interest rate risk.

Basis risk
----------

[APS 117](/standard/aps-117) includes basis risk as one of the four components of IRRBB. Basis risk is the risk of loss in earnings or economic value of the banking book arising from imperfect correlation in the adjustment of the interest rates earned and paid on different instruments with otherwise similar repricing characteristics. For the purpose of [APS 117](/standard/aps-117), this may comprise losses or gains arising from differences between the actual and expected interest margins earned by products over their implied cost of funds, over a specified holding period.

Basis risk typically includes the following exposures:

where a product interest rate moves in the same way as the implied cost of funds, but with a lead or lag. This may occur, for example, where an ADI’s repricing assumptions specify that variable rate loans reprice overnight but, in practice, interest rate changes tend to lag by several days changes in the Reserve Bank of Australia’s cash rate target;

for certain transaction accounts, the product interest rate may generally move in line with the implied cost of funds, except where the implied cost of funds falls below a low barrier. At that point, the zero floor on the customer rate forces interest margins to compress and the correlation between the product interest rate and the implied cost of funds breaks down;

non-interest bearing accounts where there is no portfolio of wholesale instruments that can replicate the lack of variation in the product rate. There will always, therefore, be deviations between the movement of the accounts’ interest rate and that of the implied cost of funds;

products where there is no portfolio that can accurately model the movement of the product customer interest rate in all circumstances. This may include items such as deeming accounts and mortgages that have capped, but not fixed, rates;

where repricing assumptions for a product are poorly chosen, large differences may arise between the movement of the product rate and that of the implied cost of funds and generate material basis risk gains and losses;

in the case where repricing assumptions provide a good fit for the product interest rate, there will usually be an error term representing unavoidable, random, residual deviations between the movement of the product rate and that of the implied cost of funds; and

where the interest rate on a banking book item is based on a different yield curve from the one used to analyse repricing and yield curve risks. A Commonwealth Government bond held in the banking book, for example, will price off the government yield curve, which is similar, but not identical, to the swap curve used by many ADIs to assess IRRBB.

|  |  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Table 1: Expected interest rates (for the 12 months to June) | | | | | | | |  |  |  |  |  |
| Expected  interest rates (% p.a.) | July | Aug | Sep | Oct | Nov | Dec | Jan | Feb | Mar | Apr | May | Jun |
| Implied cost of funds | 5.14 | 5.18 | 5.24 | 5.29 | 5.36 | 5.42 | 5.49 | 5.57 | 5.64 | 5.70 | 5.76 | 5.82 |
| Product rate | 1.50 | 1.52 | 1.55 | 1.58 | 1.60 | 1.62 | 1.64 | 1.65 | 1.66 | 1.68 | 1.69 | 1.71 |
| Margin | 3.64 | 3.66 | 3.69 | 3.71 | 3.76 | 3.80 | 3.85 | 3.92 | 3.98 | 4.02 | 4.07 | 4.11 |

For the purpose of [APS 117](/standard/aps-117), basis risk would typically not include variations in repricing caused by customers behaving differently from what is assumed in the repricing assumptions as such variations would generally be classified as optionality risk.

### Numerical example of basis risk

Consider the case of a transaction account that pays different rates of interest (set at the ADI’s discretion) on different tiered balances, with most tiers paying interest several percentage points below wholesale rates. The repricing assumption for this portfolio might be that it reprices in 12 equal tranches at intervals from one to 12 months into the future. These assumptions may have been chosen as a reasonable, simplified approximation of the way the product’s average interest rate[2] has been observed to change over time.

[2]

Average interest rate for a period is total interest paid over the period, divided by average balance, across all accounts.

The ADI may have expectations of interest rates for the next 12 months as shown in Table 1 below. The implied cost of funds is based on a rolling average of 12-month rates, consistent with the ADI’s repricing assumption.

Actual interest rates may move over the 12-month period as shown in Table 2. The bottom two rows show the difference between actual and expected margins, which is a loss over the 12-month period of 0.45 per cent of the average of the monthly total balances. This is the product loss from basis risk over the period.

|  |  |  |  |  |  |  |  |  |  |  |  |  |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Table 2: Actual interest rates (for the 12 months to June) | | | | | | | | | | | | |
| Actual interest rates (% p.a.) | July | Aug | Sep | Oct | Nov | Dec | Jan | Feb | Mar | Apr | May | Jun |
| Implied cost of funds | 5.14 | 5.09 | 5.04 | 4.99 | 4.94 | 4.89 | 4.84 | 4.79 | 4.74 | 4.69 | 4.64 | 4.59 |
| Product rate | 1.50 | 1.51 | 1.52 | 1.51 | 1.50 | 1.48 | 1.46 | 1.44 | 1.42 | 1.41 | 1.40 | 1.40 |
| Margin | 3.64 | 3.58 | 3.52 | 3.48 | 3.44 | 3.41 | 3.38 | 3.35 | 3.32 | 3.28 | 3.24 | 3.19 |
| Margin  shortfall[3] | 0.00 | 0.08 | 0.17 | 0.23 | 0.32 | 0.39 | 0.47 | 0.57 | 0.66 | 0.74 | 0.83 | 0.92 |
| Cumulative shortfall | 0.00 | 0.01 | 0.02 | 0.04 | 0.07 | 0.10 | 0.14 | 0.19 | 0.24 | 0.30 | 0.37 | 0.45 |

[3]

This is the difference between the expected margin and the actual margin.

Optionality risk
----------------

[APS 117](/standard/aps-117) includes optionality risk as one of the four components of IRRBB. Optionality risk in the banking book is the risk of losses arising due to the existence of stand-alone or embedded options[4] in banking book items, to the extent that the potential for those losses is excluded from the measurement of repricing, yield curve or basis risks. In the case of options embedded in customer products, it will generally arise from customers exercising choices that cause the actual product repricing dates to deviate from those specified in the ADI’s repricing assumptions.

[4]

An option provides the holder the right, but not the obligation, to buy, sell, or in some manner alter the cash flow of an instrument or financial contract.

Optionality risk typically includes the following exposures:

where an ADI’s customers make greater (lower) than expected levels of fixed-rate loan prepayments after an interest rate decline (rise), and the full economic cost of prepayment is not charged to the customer;

where customers make greater-than-expected net withdrawals from nil or low-interest, at-call deposit accounts following an interest rate rise, and funds from those accounts have been invested at term by the ADI;

where customers decline to drawdown on rate-lock facilities[5] where the interest rate has reduced since taking out the facility; and

[5]

A rate-lock facility provides a borrower, at the time of loan approval, the option of drawing down on a loan at a guaranteed interest rate. The option will typically have a defined period of, for example, 90 days.

interest rate options and other derivatives or securities with option characteristics.

The lack of a causal relationship between interest rate changes and customers’ exercise of embedded options does not necessarily mean that there is no optionality risk. Balances in a particular non-interest bearing account may, for example, vary between quarters in a way that is unrelated to interest rates and therefore no correlation would be observed. Nevertheless, if that random balance variation gives an unusually sharp drop in the balance of the portfolio in a quarter that follows a quarter with a large rise in interest rates, the ADI will generally incur losses as it has to sell term assets at reduced prices to pay customers’ withdrawals (assuming account balances were not invested overnight).

Fixed-interest capital instruments
----------------------------------

Under [APS 117](/standard/aps-117), an ADI’s IRRBB capital requirement is calculated as the interest rate sensitivity of the economic value of its Fundamental Tier 1 capital. Under this approach, the interest rate sensitivity of hedges over fixedinterest capital instruments are considered to be offset by the interest rate sensitivity of the instruments they hedge, as those instruments are outside of APRA’s definition of Fundamental Tier 1 capital. However, in a liquidation scenario, this offset may disappear to the extent that the capital instrument absorbs the losses. At the time of liquidation there is a risk of loss if the hedge was out of the money and this was not included in the ADI’s estimate of its IRRBB capital requirement. This risk increases as the volume and/or term of the ADI’s fixed-interest capital instruments gets larger and/or longer. As a guide, an ADI is expected to consider this risk in assessing its overall IRRBB exposure.

Interest rate risk in the banking book management framework
-----------------------------------------------------------

[APS 117](/standard/aps-117) states that an ADI’s IRRBB measurement system must be closely integrated into the ADI’s risk management processes. APRA is aware that most ADIs, in their own calculations for economic capital and risk limit comparisons, use different holding periods and confidence levels for the measurement of repricing and yield curve risk from that prescribed in [APS 117](/standard/aps-117) for the purpose of determining the IRRBB capital requirement. APRA does not generally consider such differences to be a failure to integrate the risk measurement system, as long as the same system is used for both purposes, with only the parameters differing.

[APS 117](/standard/aps-117) states that an ADI’s IRRBB measurement system must monitor the ADI’s risk profile in terms of earnings at risk and economic value sensitivity. As good practice, APRA envisages that this process would occur on at least a monthly basis and that the results of this process would also be reviewed on a monthly basis by the senior management committee detailed in [Attachment A to APS 117](/standard/aps-117#Attachment-A).

[Attachment A to APS 117](/standard/aps-117#Attachment-A) states that an ADI’s Board of directors, or committee thereof, must review on a regular basis IRRBB management reports and satisfy itself that this risk is being appropriately managed. As good practice, APRA envisages that such reviews would occur on at least a quarterly basis.

[Attachment A to APS 117](/standard/aps-117#Attachment-A) requires periodic independent reviews of an ADI’s framework for managing IRRBB. As a guide, such a review would typically involve an assessment of whether the IRRBB management framework and measurement system is being implemented effectively across the ADI, and the review would include an assessment of:

the accuracy and adequacy of the ADI’s policies and supporting documentation for managing and measuring IRRBB as well as the ADI’s compliance with, and consistent application of, those policies and documentation;

compliance with the requirements of [APS 117](/standard/aps-117);

the structure and resources of the risk management unit;

the scope of IRRBB captured by the measurement system and an assessment of whether the system captures all material IRRBB exposures from all relevant geographic locations;

the consistency, timeliness, reliability and completeness of data that are incorporated into the model, including the independence of such data sources;

the robustness and mathematical correctness of the model and the reasonableness of assumptions made in the model or elsewhere in the measurement system, such as interest rate volatility and correlation assumptions, distributional assumptions, cross-currency assumptions and assumptions about customer behaviour, including repricing assumptions;

the integrity of the management information system, including the appropriateness and accuracy of the management reports related to the output of the model;

the adequacy of the ADI’s model performance testing;

the robustness and adequacy of the ADI’s stress testing program;

the appropriateness of model validation processes, including the adequacy of procedures and controls over changes in model inputs, assumptions and calculation methodologies and assessment of the operation of those processes and validation of any significant change in the measurement system; and

the integration of the measurement system into daily IRRBB management processes.

Related standards, guidance and other information
-------------------------------------------------

Related documents give you more information about the document you’ve been reading. The documents listed on this page might:

* provide guidance or information on your requirements
* cover a similar topic
* be in the same pillar of the framework.

Links to referenced documents, definitions, footnotes and other information are provided in-line as you read the original document.

### Prudential standard

Document[CPS 220 Risk Management](/standard/cps-220)

CPS 220 Risk Management requires all entities (excluding RSE licensees) to maintain a risk management framework that covers all material risks.

Industry

Banking, General insurance, Life insurance, Private health insurance

Document typePrudential standard

Status

Current

Pillar

Risk Management

Document[APS 117 Interest Rate Risk in the Banking Book](/standard/aps-117)

APS 117 Capital Adequacy: Interest Rate Risk in the Banking Book (Advanced ADIs) requires internal ratings-based approach (IRB) ADIs to maintain adequate capital for its interest rate risk.

Industry

Banking

Document typePrudential standard

Status

Current

Pillar

Financial Resilience

### Prudential practice guide

Document[APG 117 Interest Rate Risk in the Banking Book](/ppg/apg-117-final-not-force)

APG 117 Interest Rate Risk in the Banking Book provides guidance for ADIs on APS 117 Interest Rate Risk.

Industry

Banking

Document typePrudential practice guide

Status

Final not yet in force

Pillar

Financial Resilience

More information
----------------

You can find more information, organised by industry, on the APRA website. Go to the website to access:

* reporting standards
* consultation documents
* statistical publications
* news and other publications (including speeches).

[Go to APRA’s website](https://www.apra.gov.au/)

Prudential framework pillars

Financial Resilience

Capital

Supporting

[Open consultations](https://www.apra.gov.au/#open-consultations)

All consultations

* [Banking
  consultations](https://www.apra.gov.au/consultations/1)

[Notify a breach](https://www.apra.gov.au/notify-a-breach)