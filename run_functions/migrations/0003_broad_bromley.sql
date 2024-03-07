-- Custom SQL migration file, put you code below! --

insert into vendors (id, title) values ('replicate', 'Replicate') on conflict do nothing;--> statement-breakpoint
insert into vendors (id, title) values ('mystic', 'Mystic.ai') on conflict do nothing;--> statement-breakpoint
insert into vendors (id, title) values ('modal', 'Modal.com') on conflict do nothing;
