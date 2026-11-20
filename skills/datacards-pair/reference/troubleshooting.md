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

## A kernel that hangs

A kernel runs one thing at a time. While a cell runs, or a call of yours
does, every further call waits. Signs: `execute-code.sh` does not return,
or ends with "Execution did not complete"; the notebook shows a cell that
has been running for a long time.

1. **Stop the call that waits.** Ending `execute-code.sh` (a timeout, an
   interrupt) interrupts the kernel, as the stop button in the notebook
   does. That ends most loops and sleeps.
2. **Try a small call**, such as `-c "print(1)"`. If it answers, the kernel
   is back: go on, and fix what blocked.
3. **Restart the kernel** when it still does not answer. Send the call on
   its own:

   ```bash
   bash scripts/execute-code.sh --url <url> --file <path as listed> \
     -c "import marimo._code_mode as cm; cm.restart_kernel()"
   ```

   It prints "Kernel restarted". The server carries it out, the kernel is
   not asked, so this works when nothing else does. With other code in the
   same call it is not a restart: the kernel gets the call and raises an
   error that says so.

After a restart the kernel is new: no variables, no imports, no cell has
run. The notebook's code is unchanged, and the outputs on screen are the
ones from before the restart until the cells run again. A process that was
running through the notebook is aborted, with every notebook it was running;
notebooks outside that process are not affected. Start over with `help(cm)`,
then run the cells you need. Tell the user that you restarted the kernel,
and why: what they had in memory is gone too.

Do not restart to get rid of an error message. A restart loses work and
fixes only a kernel that is stuck or whose state is beyond repair (a
library that cached a wrong state at import, see
[gotchas.md](gotchas.md)).

An older DataCards server does not know the call: the kernel answers
`module 'marimo._code_mode' has no attribute 'restart_kernel'`. Then ask the
user to restart the kernel from the notebook (the restart button at the
bottom right, or "Restart kernel" in the command palette).

## A kernel that died

A kernel can die under a call: a library crashes in native code
(segmentation fault), the machine runs out of memory, the code calls
`os._exit`. The call then ends at once, with exit code 1 and a message that
starts with "The kernel died while the code ran" and names the cause.

There is nothing to restart: DataCards has already given the notebook a
fresh kernel, and your next call runs in it. As after a restart, it has no
variables and no imports, no cell has run in it, and a process that was
running through the notebook is aborted. A user who has the notebook open
sees a "Kernel stopped" box with the cause and a Restart button.

Do not send the same code again to see whether it works this time: it kills
the fresh kernel as well. Find the line first, by running the steps one at a
time, smallest first. Then tell the user what crashed the kernel, and that
what they had in memory is gone.

An older DataCards server gives no message: the call waits until its
timeout, and the notebook does not answer afterwards. A restart from an
agent does not help there. Ask the user to restart the kernel from the
notebook and to reload the page; if `dc.data.publish` and `dc.data.consume`
time out in that notebook after that, the project has to be restarted.

## Reading common messages

- **`Timeout waiting for acknowledgment after 5.0 seconds`** on
  `dc.data.publish` / `dc.data.consume`: the data catalog did not answer.
  This is usually not an error in the cell. Seen causes: the notebook's node
  is missing from the graph (the system log shows `NodeNotFound`), or the
  notebook service restarted and lost its connection. Check whether the same
  line works in another notebook; if it does, the notebook is affected, not
  the code.
- **`The kernel died while the code ran`**: your call, or a cell that ran at
  the same time, crashed the kernel. See
  [A kernel that died](#a-kernel-that-died).
- **`An ancestor raised an exception`**: a cell upstream failed. Find the
  first failing cell (`ctx.cells[...].errors`); if it is a publish/consume
  timeout, see above.
- **`Key not found`** on consume: the publishing cell has not run, or its
  publish failed.
- **`No active sessions`** from the script: no notebook is open. In an empty
  project a human has to create the first notebook.
