import React from "react"
import ApiClient from "../../api/ApiClient";
import {
  Button,
  CircularProgress,
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
}

class Jobs extends React.Component<Props, State> {
  constructor(props) {
    super(props);
    this.state = {
      loading: true,
      modules: [],
      jobRuns: [],
      module: "",
      argsString: "{}"
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
        <FormGroup style={{marginBottom: 12}}>
          <FormControl>
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
          <FormControl>
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
          <FormControl>
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
                      <Input
                        multiline={true}
                        rows={3}
                        rowsMax={3}
                        disabled={true}
                        value={jobRun.drained_log_lines.map(l => `> ${l}`).join("\n")}
                        style={{fontFamily: "monospace"}}
                      />
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </TableContainer>
      </React.Fragment>
    )
  }
}

export default Jobs
