# Troubleshooting Inside a Project

For problems reaching or selecting a session see
[execution-context.md](execution-context.md).

## The sandbox

A cloud project runs in its own Linux sandbox. From the kernel you can run
shell commands as a non-root user (`subprocess`), look at the process list
and memory (`ps`, `free`), and read the system log (`journalctl`). This is
where the answer usually is when something hangs.

## Look at the system early

Error messages in a notebook often suggest a bug in your own code when the
cause is outside the notebook. After two failed attempts to fix a problem in
the code, stop rebuilding and check, from the kernel:

1. Memory and process list: is the sandbox out of memory, are there leftover
   processes?
2. The system log: restarts, "Out of memory", errors from the DataCards
   services.

Report cleanly: what is proven, what is an assumption, and what you caused
yourself.

## Reading common messages

- **`Timeout waiting for acknowledgment after 5.0 seconds`** on
  `dc.data.publish` / `dc.data.consume`: the data catalog did not answer.
  This is usually not an error in the cell. Seen causes: the notebook's node
  is missing from the graph (the system log shows `NodeNotFound`), or the
  notebook service restarted and lost its connection. Check whether the same
  line works in another notebook; if it does, the notebook is affected, not
  the code.
- **`An ancestor raised an exception`**: a cell upstream failed. Find the
  first failing cell (`ctx.cells[...].errors`); if it is a publish/consume
  timeout, see above.
- **`Key not found`** on consume: the publishing cell has not run, or its
  publish failed.
- **`No active sessions`** from the script: no notebook is open. In an empty
  project a human has to create the first notebook.
