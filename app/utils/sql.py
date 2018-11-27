ADD_TRIGGER = '''begin;

create or replace function notify_task ()
 returns trigger
 language plpgsql
as $$
declare
  channel text := TG_ARGV[0];
begin
  PERFORM (
    with payload(id) as
    (
       select NEW.id
    )
    select pg_notify(channel, row_to_json(NEW.*)::text)
       from payload
  );
  RETURN NULL;
end;
$$;

CREATE TRIGGER task_modified
        AFTER INSERT
            ON task
        FOR EACH ROW
            EXECUTE PROCEDURE notify_task('data');

commit;
'''