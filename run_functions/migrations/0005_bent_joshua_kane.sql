-- Custom SQL migration file, put you code below! --
insert into vendors (id, title) values ('runpod', 'Runpod') on conflict do nothing;--> statement-breakpoint
insert into vendors (id, title) values ('beam', 'Beam') on conflict do nothing;--> statement-breakpoint
insert into vendors (id, title) values ('modelz', 'Modelz.ai') on conflict do nothing;
