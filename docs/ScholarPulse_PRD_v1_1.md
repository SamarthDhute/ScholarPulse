# ScholarPulse --- Product Requirements Document (PRD)

  -----------------------------------------------------------------------
  Document field                      Details
  ----------------------------------- -----------------------------------
  Product name                        ScholarPulse

  Document type                       Non-technical Product Requirements
                                      Document

  Version                             1.1

  Status                              Proposed

  Intended audience                   Student developer, academic guide,
                                      evaluators and product stakeholders

  Document rule                       Every requirement is described in
                                      terms of **what** the product
                                      should do and **why** it matters.
                                      Technical implementation details
                                      are excluded.
  -----------------------------------------------------------------------

## 1. Product Overview

  ------------------------------------------------------------------------
  ID                Field             What               Why
  ----------------- ----------------- ------------------ -----------------
  PO-01             Product concept   ScholarPulse is an Gives users one
                                      intelligent        coherent place to
                                      research discovery discover papers
                                      and                and explore
                                      knowledge-mining   research
                                      platform for       patterns.
                                      finding, exploring 
                                      and understanding  
                                      academic research  
                                      papers.            

  PO-02             Primary users     Students, research Identifies who
                                      students, faculty  the product is
                                      members, project   designed to help.
                                      evaluators and     
                                      authorized         
                                      administrators.    

  PO-03             Core problem      Finding relevant   Establishes the
                                      research papers    user problem the
                                      can be             product must
                                      time-consuming,    solve.
                                      and understanding  
                                      relationships      
                                      between papers and 
                                      topics can be      
                                      difficult.         

  PO-04             Product promise   Help users         Defines the
                                      discover relevant  expected user
                                      research, explore  benefit.
                                      related topics and 
                                      understand         
                                      research           
                                      collections        
                                      through useful     
                                      results and clear  
                                      insights.          

  PO-05             Product boundary  Focus on research  Keeps
                                      discovery and      expectations
                                      dataset-level      accurate and
                                      insights; do not   scope manageable.
                                      claim to verify    
                                      scientific truth   
                                      or replace         
                                      original           
                                      publications.      
  ------------------------------------------------------------------------

## 2. Problem Statement

  -----------------------------------------------------------------------
  ID                      What is the problem?    Why does it matter?
  ----------------------- ----------------------- -----------------------
  PS-01                   Users struggle to find  Relevant information
                          relevant papers across  can be missed and
                          large research          literature exploration
                          collections.            takes longer.

  PS-02                   Basic keyword searches  Users need to reach
                          may return results in   useful papers sooner
                          an unhelpful order.     and spend less time on
                                                  irrelevant results.

  PS-03                   Papers are often        Users need to discover
                          explored individually   connected topics,
                          rather than as related  similar papers and
                          groups.                 recurring keywords.

  PS-04                   Research records may be Poor data quality
                          incomplete,             reduces trust in
                          inconsistent or         results and distorts
                          duplicated.             analytics.

  PS-05                   Research trends and     Users need clear
                          search quality can be   summaries and
                          difficult to interpret. measurable evidence of
                                                  usefulness.

  PS-06                   Students need one       The product should
                          practical project that  produce explainable
                          demonstrates both       outputs suitable for
                          Information Retrieval   academic evaluation.
                          and Data Science.       
  -----------------------------------------------------------------------

## 3. Product Goals and Success Measures

  -----------------------------------------------------------------------
  Goal ID           What should be    Why?              How success will
                    achieved?                           be assessed
  ----------------- ----------------- ----------------- -----------------
  G-01              Help users        Research          A defined set of
                    discover relevant discovery is the  test queries
                    research papers.  primary product   returns relevant
                                      value.            results.

  G-02              Make result       Users need useful Search quality
                    ordering useful   rankings and      metrics are
                    and measurable.   evaluators need   reported for a
                                      evidence.         judged test set.

  G-03              Reveal groups and Topic exploration Topic clusters
                    relationships     can help users    and keyword
                    within research.  discover          associations can
                                      unfamiliar areas. be inspected.

  G-04              Present           Visual summaries  Users can view
                    collection        make patterns     publication,
                    insights clearly. easier to         category, cluster
                                      understand.       and keyword
                                                        summaries.

  G-05              Provide a         The project       Core journeys
                    dependable        should support    pass agreed
                    product           demonstration and acceptance checks
                    foundation.       future extension. and failures are
                                                        communicated.

  G-06              Demonstrate both  The project must  Delivered
                    academic          show meaningful   capabilities are
                    subjects.         practical         mapped to
                                      coverage of both  relevant units
                                      syllabi.          with evidence.
  -----------------------------------------------------------------------

## 4. Target Users

  -----------------------------------------------------------------------
  Persona ID        Who is the user?  What do they      Why does
                                      need?             ScholarPulse
                                                        help?
  ----------------- ----------------- ----------------- -----------------
  U-01              Student           Find papers for   Reduces manual
                                      assignments,      searching and
                                      seminars and      supports
                                      projects; explore literature
                                      related topics.   exploration.

  U-02              Research student  Discover relevant Supports a more
                                      papers, compare   organized
                                      topics and keep   research
                                      track of useful   workflow.
                                      records.          

  U-03              Faculty member /  Review research   Provides
                    academic guide    collections and   searchable
                                      inspect           records and clear
                                      topic-level       summaries.
                                      patterns.         

  U-04              Project evaluator Inspect practical Makes intended
                                      IR and Data       capabilities and
                                      Science outcomes. measurable
                                                        outputs visible.

  U-05              Authorized        Identify          Helps maintain
                    administrator     data-quality      the quality and
                                      issues and review reliability of
                                      collection        the collection.
                                      updates.          
  -----------------------------------------------------------------------

## 5. Product Scope

### 5.1 In Scope

  ------------------------------------------------------------------------------------
  Requirement ID Capability       What should it do? Why is it needed?  Priority
  -------------- ---------------- ------------------ ------------------ --------------
  S-01           Research         Maintain a         Search and         Must
                 collection       searchable         analysis depend on 
                                  collection of      a consistent       
                                  academic paper     collection.        
                                  records and                           
                                  available                             
                                  metadata.                             

  S-02           Data quality     Identify           Improves trust in  Must
                                  incomplete and     results and        
                                  duplicate records  analytics.         
                                  and preserve                          
                                  available source                      
                                  information.                          

  S-03           Search           Let users search   Search is the main Must
                                  research records   entry point to the 
                                  using keywords and product.           
                                  supported query                       
                                  conditions.                           

  S-04           Ranked results   Order results by   Helps users find   Must
                                  relevance and show useful papers      
                                  useful summaries.  earlier.           

  S-05           Search filters   Refine results by  Helps users narrow Must
                                  available fields   broad searches.    
                                  such as year,                         
                                  author, category                      
                                  and keywords.                         

  S-06           Paper details    Show available     Gives users        Must
                                  title, authors,    context to judge   
                                  abstract, year,    relevance.         
                                  keywords, source                      
                                  and publication                       
                                  identifiers.                          

  S-07           Classification   Assign or display  Supports browsing  Must
                                  research           and demonstrates a 
                                  categories and     practical Data     
                                  communicate that   Science use case.  
                                  predictions may be                    
                                  model-generated.                      

  S-08           Clustering       Group similar      Reveals themes     Must
                                  papers and let     beyond existing    
                                  users explore the  labels.            
                                  groups.                               

  S-09           Association      Show keyword       Helps users        Must
                 mining           co-occurrence      discover           
                                  patterns with      relationships      
                                  support,           between terms.     
                                  confidence and                        
                                  lift.                                 

  S-10           Research         Display            Makes              Must
                 analytics        publication        collection-level   
                                  trends, category   patterns easier to 
                                  distribution,      interpret.         
                                  cluster summaries                     
                                  and keyword                           
                                  insights.                             

  S-11           Search           Compare retrieval  Search quality     Must
                 evaluation       approaches using   should be          
                                  defined queries    evidenced, not     
                                  and relevance      merely asserted.   
                                  judgments.                            

  S-12           Related papers   Suggest papers     Helps users        Should
                                  related to a       continue           
                                  viewed paper or    exploring.         
                                  selected topic.                       

  S-13           Saved library    Let users save     Supports ongoing   Should
                                  papers for later   academic work.     
                                  review.                               

  S-14           Research data    Allow research     Keeps the          Should
                 updates          records to be      collection         
                                  added or refreshed maintainable       
                                  while retaining    beyond a one-time  
                                  source             demonstration.     
                                  information.                          

  S-15           Data health view Let authorized     Helps maintainers  Should
                                  administrators     understand the     
                                  review collection  collection's       
                                  status, data       condition.         
                                  issues and update                     
                                  outcomes.                             

  S-16           Responsive web   Keep core journeys Users and          Must
                 experience       usable on desktop, evaluators may use 
                                  tablet and mobile  different devices. 
                                  web.                                  
  ------------------------------------------------------------------------------------

### 5.2 Out of Scope

  -----------------------------------------------------------------------
  Exclusion ID            What is excluded from   Why is it excluded?
                          Version 1?              
  ----------------------- ----------------------- -----------------------
  O-01                    Generating complete     ScholarPulse is a
                          research papers for     discovery and analysis
                          users.                  product, not an
                                                  academic-writing
                                                  generator.

  O-02                    Guaranteeing scientific Search and metadata
                          correctness of a        analysis do not
                          paper's claims.         establish scientific
                                                  validity.

  O-03                    Hosting or              Source rights and
                          redistributing          access restrictions
                          copyrighted full text   must be respected.
                          without permission.     

  O-04                    Large-scale             It would increase
                          unrestricted web        operational, compliance
                          crawling.               and maintenance scope.

  O-05                    Enterprise-scale        The initial product is
                          distributed             a solo-developed
                          infrastructure.         academic project.

  O-06                    Paid subscriptions and  Monetization is not
                          billing workflows.      needed to validate the
                                                  academic product.

  O-07                    Social networking,      These do not directly
                          messaging and public    support the core
                          user profiles.          discovery and analytics
                                                  goals.

  O-08                    Treating model labels   They are analytical
                          or association rules as signals that require
                          proven scientific       interpretation.
                          conclusions.            

  O-09                    Collaborative           The first version can
                          recommendations         provide value through
                          requiring a large       paper-content
                          user-interaction        similarity.
                          history.                
  -----------------------------------------------------------------------

## 6. Functional Requirements

  -----------------------------------------------------------------------
  Requirement ID    What must the     Why is it needed? Priority
                    product do?                         
  ----------------- ----------------- ----------------- -----------------
  FR-01             Provide access to Users need a      Must
                    a collection of   consistent place  
                    academic research to discover       
                    records.          papers.           

  FR-02             Preserve          Users need to     Must
                    available source  trace records to  
                    and publication   their origins.    
                    metadata.                           

  FR-03             Identify likely   Duplicates reduce Must
                    duplicate records result quality    
                    and avoid         and distort       
                    presenting        analytics.        
                    duplicates as                       
                    unrelated papers.                   

  FR-04             Accept keyword    Users need        Must
                    queries and       flexible ways to  
                    supported query   express           
                    conditions.       information       
                                      needs.            

  FR-05             Return relevant   Result order      Must
                    results in a      affects discovery 
                    meaningful order. efficiency.       

  FR-06             Provide filters   Users need to     Must
                    and sorting using narrow and        
                    available         compare results.  
                    metadata.                           

  FR-07             Display useful    Users need        Must
                    paper summaries   context and a     
                    and available     path to the       
                    original-source   source.           
                    links.                              

  FR-08             Display research  Categories help   Must
                    categories when   users browse      
                    classification    research areas.   
                    results are                         
                    available.                          

  FR-09             Group similar     Users need to     Must
                    papers into       explore themes    
                    discoverable      beyond exact      
                    clusters.         keywords.         

  FR-10             Present keyword   Users need to     Must
                    association rules understand the    
                    with supporting   frequency and     
                    measures.         strength of       
                                      keyword           
                                      co-occurrence.    

  FR-11             Present           Users need to     Must
                    collection        interpret         
                    insights in       patterns without  
                    readable charts   inspecting every  
                    and summaries.    record.           

  FR-12             Report search and Users and         Must
                    model evaluation  evaluators need   
                    results.          evidence of       
                                      quality and       
                                      limitations.      

  FR-13             Offer             Helps users       Should
                    related-paper     continue research 
                    suggestions when  exploration.      
                    sufficient                          
                    information                         
                    exists.                             

  FR-14             Allow users to    Supports personal Should
                    save papers when  organization and  
                    a personal        later review.     
                    library is                          
                    available.                          

  FR-15             Communicate empty Helps users       Must
                    results,          understand what   
                    unavailable       happened and how  
                    metadata and      to proceed.       
                    recoverable                         
                    failures clearly.                   

  FR-16             Show data-update  Supports          Should
                    and data-quality  collection        
                    status to         maintenance.      
                    authorized                          
                    administrators.                     
  -----------------------------------------------------------------------

## 7. User Stories

  -----------------------------------------------------------------------------
  Story ID       User role       What does the    Why does the   Priority
                                 user want?       user want it?  
  -------------- --------------- ---------------- -------------- --------------
  US-01          Student         Search papers by To find        Must
                                 topic.           research       
                                                  relevant to an 
                                                  assignment or  
                                                  project.       

  US-02          Student         See results      To review the  Must
                                 ordered by       most useful    
                                 relevance.       papers first.  

  US-03          Student         Filter results   To narrow the  Must
                                 by year, author  search to      
                                 or category.     suitable       
                                                  papers.        

  US-04          Student         Read available   To judge       Must
                                 abstracts and    relevance      
                                 metadata.        before opening 
                                                  a source.      

  US-05          Research        Explore papers   To discover    Should
                 student         similar to a     related work.  
                                 selected paper.                 

  US-06          Research        Explore groups   To identify    Must
                 student         of similar       themes in a    
                                 papers.          research area. 

  US-07          Research        View related     To identify    Must
                 student         keyword          terms that     
                                 patterns.        frequently     
                                                  appear         
                                                  together and   
                                                  refine         
                                                  exploration.   

  US-08          Student         View publication To understand  Must
                                 trends by year   how the        
                                 or topic.        collection is  
                                                  distributed    
                                                  over time.     

  US-09          Project         Compare          To assess      Must
                 evaluator       retrieval        search quality 
                                 methods using    objectively.   
                                 evaluation                      
                                 metrics.                        

  US-10          Project         Review           To assess the  Must
                 evaluator       classification   Data Science   
                                 and clustering   components.    
                                 quality                         
                                 indicators.                     

  US-11          User            Receive clear    To understand  Must
                                 feedback when no the result and 
                                 papers match a   revise the     
                                 query.           search.        

  US-12          User            Save useful      To return to   Should
                                 papers.          them later.    

  US-13          Administrator   Identify         To maintain    Should
                                 incomplete or    collection     
                                 duplicate        quality.       
                                 records.                        

  US-14          Administrator   See whether a    To respond to  Should
                                 data update      collection     
                                 succeeded or     problems.      
                                 failed.                         

  US-15          User            Use the main     To access      Must
                                 experience on a  ScholarPulse   
                                 phone or         on a           
                                 computer.        convenient     
                                                  device.        
  -----------------------------------------------------------------------------

## 8. Core User Journeys

  ------------------------------------------------------------------------
  Journey ID        What does the     What outcome       Why is this
                    user do?          should occur?      journey
                                                         important?
  ----------------- ----------------- ------------------ -----------------
  J-01 --- Find     Search, refine    User can inspect   This is the
  research          results and open  relevant papers    primary product
                    a paper record.   and their source   journey.
                                      details.           

  J-02 --- Explore  Open a paper or   User discovers     Supports
  a topic           topic group and   related research.  exploration
                    inspect related                      beyond one
                    papers or                            result.
                    keywords.                            

  J-03 ---          Open research     User understands   Connects
  Understand        analytics and     collection-level   discovery with
  patterns          inspect           patterns.          Data Science
                    publication,                         insights.
                    category, cluster                    
                    and keyword                          
                    summaries.                           

  J-04 --- Evaluate Open the          User can inspect   Demonstrates
  search            evaluation view   results on a       measurable IR
                    and compare       defined test set.  outcomes.
                    retrieval                            
                    approaches.                          

  J-05 --- Review   Inspect           User can           Demonstrates
  model outcomes    classification,   understand the     measurable Data
                    clustering and    outputs and their  Science outcomes.
                    association       limitations.       
                    outputs with                         
                    quality                              
                    indicators.                          

  J-06 --- Maintain Authorized        Issues and update  Supports
  collection        administrator     outcomes are       reliability
                    reviews data      visible.           beyond a one-time
                    quality and                          demo.
                    update status.                       

  J-07 --- Return   Open the saved    User can revisit   Supports ongoing
  to saved research library and       useful records.    academic work.
                    select a saved                       
                    paper.                               
  ------------------------------------------------------------------------

## 9. Business Rules

  -----------------------------------------------------------------------
  Rule ID                 What is the rule?       Why does it matter?
  ----------------------- ----------------------- -----------------------
  BR-01                   Preserve an available   Supports traceability.
                          original-source         
                          reference for each      
                          paper record.           

  BR-02                   Show missing metadata   Prevents misleading
                          as unavailable instead  users.
                          of inventing it.        

  BR-03                   Do not silently merge   Similar papers can be
                          records when duplicate  distinct publications.
                          identity is uncertain.  

  BR-04                   Do not present          Relevance and
                          relevance scores as     scientific validity are
                          probabilities of        different.
                          scientific correctness. 

  BR-05                   Identify predicted      Helps users interpret
                          categories as           the result correctly.
                          model-generated when    
                          they are not verified   
                          labels.                 

  BR-06                   Present clusters and    Dataset patterns can be
                          association rules as    incomplete or biased.
                          patterns in the         
                          available dataset, not  
                          universal truths.       

  BR-07                   Support evaluation      Makes claims credible
                          claims with a           and reproducible.
                          documented test set and 
                          reported metrics.       

  BR-08                   Explain that            Similarity does not
                          related-paper           establish quality or
                          suggestions indicate    authority.
                          similarity, not         
                          endorsement.            

  BR-09                   Respect source terms,   Encourages responsible
                          applicable access       data collection.
                          restrictions and        
                          content rights.         

  BR-10                   Keep core discovery     Maintains feasibility
                          useful without          for solo development.
                          requiring extensive     
                          user-interaction        
                          history.                
  -----------------------------------------------------------------------

## 10. Acceptance Criteria

  -----------------------------------------------------------------------
  Criterion ID            What must be true for   Why does it matter?
                          acceptance?             
  ----------------------- ----------------------- -----------------------
  AC-01                   A user can submit a     Confirms the core
                          supported query and     discovery journey.
                          receive paper records   
                          or a clear no-results   
                          state.                  

  AC-02                   Results show available  Makes results
                          metadata and a source   interpretable and
                          reference.              traceable.

  AC-03                   Supported filters       Confirms search
                          narrow results          refinement works.
                          according to selected   
                          criteria.               

  AC-04                   Boolean, TF-IDF and     Shows practical
                          BM25 outcomes can be    coverage of core IR
                          demonstrated and        concepts.
                          compared.               

  AC-05                   Search metrics can be   Supports credible
                          reproduced from defined comparisons.
                          test queries and        
                          relevance judgments.    

  AC-06                   Classification results  Demonstrates tested
                          and evaluation measures classification.
                          are available on a      
                          held-out evaluation     
                          set.                    

  AC-07                   Similarity-based        Makes clustering
                          clusters can be         interpretable.
                          inspected and relevant  
                          quality indicators are  
                          available.              

  AC-08                   Association rules show  Demonstrates
                          support, confidence and association mining.
                          lift for the selected   
                          dataset.                

  AC-09                   Analytics summaries are Ensures charts reflect
                          derived from the        actual data.
                          available research      
                          records.                

  AC-10                   Missing data and failed Protects user trust.
                          operations are          
                          communicated without    
                          false success claims.   

  AC-11                   Users can open          Supports further
                          available               research.
                          original-source         
                          references.             

  AC-12                   Core journeys are       Supports real usage and
                          usable on desktop and   demonstrations.
                          mobile web layouts.     

  AC-13                   Administrative          Protects maintenance
                          data-health information operations.
                          is available only to    
                          authorized users.       

  AC-14                   Project documentation   Prevents overclaiming
                          explains dataset        and supports academic
                          limitations, evaluation review.
                          methods and known gaps. 
  -----------------------------------------------------------------------

## 11. Non-Functional Product Expectations

  -----------------------------------------------------------------------
  Expectation ID    Quality area      What is expected? Why?
  ----------------- ----------------- ----------------- -----------------
  NFR-01            Usability         Core actions and  Reduces
                                      navigation are    confusion.
                                      understandable to 
                                      first-time users. 

  NFR-02            Responsiveness    Main journeys     Supports varied
                                      remain usable on  devices.
                                      desktop, tablet   
                                      and mobile web.   

  NFR-03            Reliability       Failures are      Maintains trust.
                                      communicated      
                                      clearly and       
                                      incorrect success 
                                      states are        
                                      avoided.          

  NFR-04            Data integrity    Paper metadata,   Protects
                                      source references collection
                                      and saved records usefulness.
                                      remain            
                                      consistent.       

  NFR-05            Transparency      Model outputs,    Helps users
                                      relevance scores  interpret results
                                      and analytical    responsibly.
                                      patterns are      
                                      described without 
                                      overstatement.    

  NFR-06            Privacy           Personal          Protects user
                                      libraries and     information.
                                      account           
                                      information are   
                                      available only to 
                                      appropriate       
                                      users.            

  NFR-07            Maintainability   Future            Supports future
                                      capabilities can  development.
                                      be added without  
                                      changing the      
                                      product's core    
                                      purpose.          

  NFR-08            Accessibility     Important         Improves
                                      content, controls inclusiveness.
                                      and chart         
                                      summaries are     
                                      perceivable and   
                                      usable by a broad 
                                      range of users.   
  -----------------------------------------------------------------------

## 12. Risks and Mitigations

  ------------------------------------------------------------------------
  Risk ID           What could go      Why does it       Product-level
                    wrong?             matter?           response
  ----------------- ------------------ ----------------- -----------------
  R-01              Metadata is        Search and        Show data
                    incomplete or      analytics may be  availability and
                    inconsistent.      unreliable.       maintain
                                                         data-quality
                                                         checks.

  R-02              The dataset is too Model outputs and Document dataset
                    small or           trends may        composition and
                    unbalanced.        mislead.          avoid unsupported
                                                         claims.

  R-03              Relevance          Search metrics    Define and
                    judgments are      may not reflect   document a
                    missing or weak.   usefulness.       representative
                                                         judged test set.

  R-04              Scope becomes too  Core requirements Complete
                    large for one      may remain        Must-have
                    developer.         unfinished.       capabilities
                                                         before
                                                         Should-have
                                                         enhancements.

  R-05              Similarity results Users may         Explain that
                    are mistaken for   over-trust        recommendations
                    quality            suggestions.      indicate
                    recommendations.                     similarity, not
                                                         endorsement.

  R-06              External sources   Data updates may  Preserve source
                    change access      fail.             attribution and
                    rules or formats.                    make update
                                                         status visible.

  R-07              Charts imply       Users may draw    Show date ranges,
                    unsupported        incorrect         data coverage and
                    trends.            conclusions.      interpretation
                                                         notes.
  ------------------------------------------------------------------------

## 13. Delivery Priorities

  -----------------------------------------------------------------------
  Priority          What is included? Why is it ordered Completion
                                      this way?         outcome
  ----------------- ----------------- ----------------- -----------------
  P0 --- Core       Research records, The product must  A usable research
  discovery         data quality,     first let users   discovery
                    search, ranking,  find and inspect  journey.
                    filters and paper papers.           
                    details.                            

  P1 --- Academic   Retrieval         These demonstrate Measurable IR and
  core              comparisons,      both subjects'    Data Science
                    classification,   core concepts.    outputs.
                    clustering,                         
                    association                         
                    mining and                          
                    evaluation.                         

  P2 --- Research   Analytics, topic  Adds value after  Users can explore
  insights          exploration and   the core search   patterns and
                    related-paper     works.            related research.
                    suggestions.                        

  P3 --- Product    Saved library,    Supports ongoing  A maintainable
  foundation        administration,   use and future    product beyond
                    data updates and  extension.        the initial demo.
                    quality                             
                    improvements.                       
  -----------------------------------------------------------------------

## 14. Assumptions and Open Decisions

  ------------------------------------------------------------------------
  Decision ID       What needs to be  Current position  Why does it
                    decided?                            matter?
  ----------------- ----------------- ----------------- ------------------
  D-01              Initial content   Research-paper    Keeps Version 1
                    type              metadata, titles, focused.
                                      abstracts and     
                                      available         
                                      publication       
                                      details.          

  D-02              Dataset size      To be finalized   Affects
                                      after source and  feasibility and
                                      data-quality      evaluation.
                                      review.           

  D-03              Initial sources   Public sources    Determines data
                                      permitting the    availability,
                                      intended use;     rights and update
                                      exact sources     expectations.
                                      remain to be      
                                      confirmed.        

  D-04              User accounts     Saved-library and Defines
                                      admin features    user-facing
                                      require           access.
                                      appropriate       
                                      access controls.  

  D-05              Supported         English-first for Keeps text
                    languages         Version 1.        processing and
                                                        evaluation
                                                        manageable.

  D-06              Full-text access  Show full-text    Metadata does not
                                      links only when   guarantee
                                      lawfully          full-text access.
                                      available.        

  D-07              Performance       Set after the     Avoids arbitrary
                    targets           first dataset and claims.
                                      test queries are  
                                      defined.          

  D-08              Advanced crawling Optional after    Protects
                    and distributed   core acceptance.  solo-development
                    processing                          feasibility.
  ------------------------------------------------------------------------

## 15. Academic Syllabus Alignment

  ------------------------------------------------------------------------------
  Subject           Unit              What ScholarPulse   Why this mapping
                                      will demonstrate    matters
  ----------------- ----------------- ------------------- ----------------------
  Data Science      I ---             Structured          Establishes the nature
                    Introduction      metadata,           of the research
                                      unstructured        dataset.
                                      abstracts and data  
                                      characteristics.    

  Data Science      II --- Data       Data cleaning,      Demonstrates data
                    Warehouse and     integration,        preparation.
                    Preprocessing     reduction and       
                                      transformation      
                                      outcomes.           

  Data Science      III ---           Research            Shows predictive
                    Classification    classification;     analysis and model
                    and Regression    optional            evaluation.
                                      publication-trend   
                                      regression.         

  Data Science      IV --- Clustering K-means and         Reveals groups of
                                      hierarchical topic  similar research
                                      groups.             papers.

  Data Science      V --- Association Frequent itemsets,  Identifies keyword
                    Rule Mining       support, confidence co-occurrence
                                      and lift.           patterns.

  Data Science      VI --- Data       Publication,        Makes analytical
                    Visualization     category, cluster   results interpretable.
                                      and evaluation      
                                      charts.             

  Information       I ---             IR architecture,    Establishes the search
  Retrieval         Introduction      Boolean retrieval,  foundation.
                                      vector-space and    
                                      probabilistic       
                                      retrieval concepts. 

  Information       II ---            Inverted index,     Demonstrates efficient
  Retrieval         Dictionaries and  dictionaries, query document discovery.
                    Query Processing  processing and      
                                      ranked retrieval.   

  Information       III --- Text      Text categorization Connects retrieval
  Retrieval         Classification    and clustering      with document
                    and Clustering    outputs.            organization.

  Information       IV --- Language   Query-likelihood    Demonstrates
  Retrieval         Models            ranking and passage language-model-based
                                      retrieval.          retrieval.

  Information       V --- Web         Public metadata     Demonstrates
  Retrieval         Retrieval and     ingestion and       responsible data
                    Crawling          limited compliant   acquisition and web
                                      crawling; optional  retrieval concepts.
                                      graph ranking.      

  Information       VI --- IR         Related-paper       Demonstrates
  Retrieval         Applications      recommendations and content-based
                                      metadata            discovery and
                                      integration.        information
                                                          integration.
  ------------------------------------------------------------------------------

## 16. Definition of Product Success

  -----------------------------------------------------------------------
  Success ID              What must be achieved?  Why it defines success
  ----------------------- ----------------------- -----------------------
  SU-01                   Users can find and      Confirms the core
                          inspect relevant        product value.
                          research records.       

  SU-02                   Retrieval methods can   Demonstrates
                          be compared using a     evidence-based search
                          documented evaluation   quality.
                          set.                    

  SU-03                   Classification,         Confirms practical Data
                          clustering and          Science coverage.
                          association mining      
                          produce inspectable and 
                          evaluated outputs.      

  SU-04                   Analytics reflect the   Prevents misleading
                          available dataset and   interpretations.
                          communicate             
                          limitations.            

  SU-05                   Core journeys work      Supports usability and
                          across supported web    demonstration.
                          screen sizes.           

  SU-06                   Delivered capabilities  Supports academic
                          map to both MCA         integrity and
                          subjects without        evaluation.
                          claiming unimplemented  
                          features.               

  SU-07                   Facts, model            Supports responsible
                          predictions and         use and user trust.
                          analytical              
                          interpretations are     
                          clearly distinguished.  
  -----------------------------------------------------------------------

## 17. PRD Boundary

  -----------------------------------------------------------------------
  This document defines   This document does not  Why the boundary exists
                          define                  
  ----------------------- ----------------------- -----------------------
  What ScholarPulse       Programming languages,  These belong in a
  should do.              frameworks or           separate technical
                          libraries.              design document.

  Why each capability     Database schema, API    These are
  matters.                contracts or code       implementation
                          structure.              decisions.

  User stories,           Detailed algorithms or  The PRD remains
  priorities and          infrastructure setup    non-technical and
  acceptance criteria.    instructions.           stakeholder-readable.

  Product scope, risks    Deployment scripts or   Those belong in
  and success measures.   operational runbooks.   technical delivery
                                                  documentation.
  -----------------------------------------------------------------------

------------------------------------------------------------------------

**End of PRD --- Version 1.1**
