My Research
-------------

Background:
1) DoD creates opportunities for entities to compete
    - A contracting officer publishes the notice to SAM and can toggle the 
    'Interested Vendors List (IVL)' on or off
      - If Off, no one can join the list
    - The IVL Exists ONLY on a per notice basis

2) Entity users (us) while signed in, can click the 'Add me to interested vendors
list' on a specific notice. 
    - SAM will then pull the UEI/CAGE and the contract block from the entity registration
    - To do this, the SAM account must be connected to a SAM entity


What is a UEI / CAGE:
- Uniquie Entity Identifier (UEI)
    - A 12-character alphanumeric ID assigned to entities doing business with the U.S. federal government.
    - Issued by SAM
- Commercial and Government Entity (CAGE)
    - A 5-character alphanumeric code that identifies contractors doing business with the U.S. government.
    - Issued by DLA


What is accessible via SAM / API:
1) Account NOT linked to an entity (10 calls/day)
    1) Search open notices
        - /opportunities/v2/search, /opportunity/{id})

    2) Pull the IVL roster WITHOUT email/phone number
        - /opportunity/{id}/ivl

    3) Download public Entity Registration extract (has “Gov Business POC” e-mail)
        - Zip file, refreshed monthly

2) Account LINKED to entity (1,000 calls/day)
    - Same as above

3) With System Account:
    - All of the above AND contact block from /opportunity/{id}/ivl
    - How to get system account:
        1) Workspace > System Accounts widget (if profile meets criteria)
        2) Click Request System Account 
            - System name and description
            - Business justification for the data
            - All source-IP addresses the script will call from
            - Government sponsored POC (required for non-federal companies)
        3) Wait for GAS approval (1-3 weeks)
        4) Set password, Reveal system API key




Notice Types & IVL Behavior
-------------------------------
1) Sources Sought / RFI (r)
    - IVL use: High – Contracting officers often enable IVL to gauge industry interest.

2) Presolicitation (p)
    - IVL use: Medium – Sometimes enabled, but often off or restricted.

3) Solicitation (o)
    - IVL use: Medium/Low – Depends on agency or contracting office.

4) Combined Synopsis/Solicitation (k)
    - IVL use: Medium/Low

5) Special Notice (s)
    - IVL use: Low – Rarely has IVL enabled.

6) Award Notice (a)
    - IVL use: None – Award has already been made; IVL is irrelevant.

7) Justification & Approval / Exception Notice (u)
    - IVL use: Off – Typically sole-source or restricted cases.

8) Sale of Surplus Property (g)
    - IVL use: Off – No vendor list applies.

9) Intent to Bundle (DoD-specific) (i)
    - IVL use: Niche – Used in specific DoD procurement contexts.
