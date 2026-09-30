# Deliverable 6 pipeline results



Listings retained: 3,469. SA2 matches: 3,469. Bond rows matched: 2,673. Bond rents available: 2,673.

Prices missing: 274; usable listing price gaps: 2,474.

All 10 sanity checks passed.



## Results by quarter


### Quarter beginning 2026-04-01

Christchurch Central median Airbnb price: NZ$250.00; 117 priced listings from 119 listings.

Largest eligible median gap: Wigram North, NZ$242.71; 7 usable price gaps from 8 listings.



## Method and interpretation

Use published ALL/ALL bond totals; join by SA2 and quarter using a validated left join. Divide median weekly rent by seven. Rank only locations with at least 5 observed listing gaps. Keep missing prices and unmatched bond values as missing. Count all listings separately from priced listings.

Active tenancy bonds are a proxy, not a count of unique properties. Airbnb may include private rooms. These descriptive price gaps do not measure investment returns or establish a causal effect. Different SA2 vintages in the two inputs may explain some unmatched locations; matching codes alone does not resolve this.



## Geographic source

SA2 lookup uses the supplied Deliverable 5 cache associated with Koordinates layer 123515. Offline reproduction validates cache structure and arithmetic but does not independently verify point-in-polygon assignments or boundary-vintage compatibility.
