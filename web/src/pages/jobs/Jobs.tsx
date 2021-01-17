import React from "react"
import ApiClient from "../../api/ApiClient";
import {
  Button,
  CircularProgress, Dialog, DialogTitle,
  FormControl,
  FormGroup,
  Grid,
  Input,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Table, TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography
} from "@material-ui/core";
import JobRun from "../../api/JobRun";

interface Props {
  apiClient: ApiClient
}

interface State {
  loading: boolean,
  modules: string[],
  jobRuns: JobRun[],
  error?: Error
  module: string,
  argsString: string,
  showingLogsIndex: number
}

class Jobs extends React.Component<Props, State> {
  constructor(props) {
    super(props);
    this.state = {
      loading: true,
      modules: [],
      jobRuns: [],
      module: "",
      argsString: "{}",
      showingLogsIndex: -1
    }
  }

  componentDidMount() {
    Promise.all([
      this.props.apiClient.getOneOffJobModules(),
      this.props.apiClient.getOneOffJobRuns(),
    ])
      .then(([modules, jobRuns]) => {
        this.setState({ modules, jobRuns })
      })
      .catch(error => [
        this.setState({ error })
      ])
      .finally(() => {
        this.setState({ loading: false })
      })
  }

  onRunJob = () => {
    this.props.apiClient.runOneOffJob(this.state.module, JSON.parse(this.state.argsString))
  }

  render() {
    if (this.state.loading) {
      return (
        <Grid container justify="center">
          <CircularProgress />
        </Grid>
      )
    }
    if (this.state.error) {
      return (
        <Grid container justify="center">
          <Typography variant='body1'>
            Failed to load. Reason: {this.state.error.toString()}
          </Typography>
        </Grid>
      )
    }
    let canParseArgs = true
    try {
      JSON.parse(this.state.argsString)
    } catch {
      canParseArgs = false
    }
    return (
      <React.Fragment>
        <FormGroup>
          <FormControl margin='dense'>
            <InputLabel>Module</InputLabel>
            <Select
              value={this.state.module}
              onChange={e => {
                e.preventDefault()
                this.setState({ module: e.target.value as string })
              }}
            >
              {(this.state.modules as string[]).map((module, i) => {
                return <MenuItem key={i} value={module}>{module}</MenuItem>
              })}
            </Select>
          </FormControl>
          <FormControl margin='dense'>
            <InputLabel>Args</InputLabel>
            <Input
              value={this.state.argsString}
              onChange={e => {
                e.preventDefault()
                this.setState({argsString: e.target.value as string})
              }}
              multiline={true}
              rows={3}
              rowsMax={3}
              error={!canParseArgs}
            />
          </FormControl>
          <FormControl margin='dense'>
            <Button
              variant="contained"
              color="secondary"
              onClick={e => {
                e.preventDefault();
                this.onRunJob()
              }}
              disabled={!canParseArgs}
            >Run job</Button>
          </FormControl>
        </FormGroup>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Id</TableCell>
                <TableCell>State</TableCell>
                <TableCell>Logs</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {this.state.jobRuns.map((jobRun, i) => {
                return (
                  <TableRow key={i}>
                    <TableCell>{jobRun.job_id}</TableCell>
                    <TableCell>{jobRun.state}</TableCell>
                    <TableCell>
                      <Button
                        variant="contained"
                        color="secondary"
                        onClick={e => {
                          e.preventDefault()
                          this.setState({ showingLogsIndex: i })
                        }}
                      >Show logs</Button>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </TableContainer>
        {
          this.state.showingLogsIndex !== -1 ?
            <Dialog
              open={this.state.showingLogsIndex !== -1}
              onClose={() => {this.setState({ showingLogsIndex: -1 })}}
            >
              <DialogTitle>Logs from {this.state.jobRuns[this.state.showingLogsIndex].job_id}</DialogTitle>
              <textarea
                cols={160}
                rows={48}
                disabled
                style={{
                  fontFamily: "monospace",
                  color: "black"
                }}
                value={this.state.jobRuns[this.state.showingLogsIndex].drained_log_lines.join("\n")}
              />
            </Dialog> :
            null
        }
      </React.Fragment>
    )
  }
}

export default Jobs
