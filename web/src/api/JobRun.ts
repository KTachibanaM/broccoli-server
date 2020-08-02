export default interface JobRun {
  job_id: string
  state: string
  drained_log_lines: string[]
}
