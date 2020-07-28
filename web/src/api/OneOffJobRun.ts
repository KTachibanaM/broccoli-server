export default interface OneOffJobRun {
  job_id: string,
  state: string,
  drained_log_lines: string[]
}
