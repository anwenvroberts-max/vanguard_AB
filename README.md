# Vanguard DB -- Group Project Week 05 & 06 -- Team Ravenclaw
# Analysis of Online AB Tests  

**Project Brief** 
https://github.com/data-bootcamp-v4/lessons/blob/main/5_6_eda_inf_stats_tableau/project/project-2-brief.md
**AB Testing Info - Self Guided**
https://github.com/data-bootcamp-v4/lessons/blob/main/5_6_eda_inf_stats_tableau/project/self_guided_lessons/self_guided_ab_testing.md

**Trello Board** 
https://trello.com/invite/b/69ef3ac4836d0d1a69b3d166/ATTIa5d57dcddd8cc9418bf2ddcebb9eff3428114DD5/week-56-project

**Locked Repo to Fork**  
https://github.com/anwenvroberts-max/vanguard_AB/  

**Data sources**
1. Client Profiles -- User demographics
  (70611, 9: client_id,clnt_tenure_yr,clnt_tenure_mnth,clnt_age,gendr,num_accts,bal,calls_6_mnth,logons_6_mnth)
   https://github.com/data-bootcamp-v4/lessons/blob/main/5_6_eda_inf_stats_tableau/project/files_for_project/df_final_demo.txt
2. Digital Footprints -- User website interactions 
2.1 Part1 (343143, 5: client_id,visitor_id,visit_id,process_step,date_time)
   https://github.com/data-bootcamp-v4/lessons/blob/main/5_6_eda_inf_stats_tableau/project/files_for_project/df_final_web_data_pt_1.txt
2.2 Part2 (412266, 5: client_id,visitor_id,visit_id,process_step,date_time) -- CHECK IF THEY ARE IDENTICAL AND CAN BE MERGED 
   https://github.com/data-bootcamp-v4/lessons/blob/main/5_6_eda_inf_stats_tableau/project/files_for_project/df_final_web_data_pt_2.txt 
3. Experiment Roster -- Lists which users were part of Control or Test Group
   (70611, 2: client_id, Variation) 
   https://github.com/data-bootcamp-v4/lessons/blob/main/5_6_eda_inf_stats_tableau/project/files_for_project/df_final_experiment_clients.txt
