-- Custom SQL migration file, put you code below! --
insert into vendors (id, title) values ('inferless', 'Inferless') on conflict do nothing;
