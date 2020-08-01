import React from 'react'
import { Link } from "react-router-dom"
import ApiClient from "../../api/ApiClient";
import {
  Button,
  CircularProgress,
  Grid, IconButton, Input, MenuItem,
  Paper, Select,
  Table, TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography
} from "@material-ui/core";
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import FileCopyIcon from '@material-ui/icons/FileCopy';
import DeleteIcon from '@material-ui/icons/Delete';

interface Props {
  apiClient: ApiClient
}

interface State {
  loading: boolean,
  workers: any[],
  executors: string[],
  error?: Error
}

export default class ViewWorkersPage extends React.Component<Props, State> {
  constructor(props) {
    super(props);
    this.state = {
      "loading": true,
      "workers": [],
      "executors": []
    };
  }

  componentDidMount() {
    Promise.all([
      this.props.apiClient.getWorkers(),
      this.props.apiClient.getExecutors()
    ])
      .then(([workers, executors]) => this.setState({workers, executors}))
      .finally(() => this.setState({loading: false}))
  }

  onReplicate = (moduleName, args, intervalSeconds) => {
    window.location.replace(
      `/workers/create?module_name=${moduleName}&args=${encodeURIComponent(JSON.stringify(args))}&interval_seconds=${intervalSeconds}`
    )
  }

  onRemove = workerId => {
    if (window.confirm(`Are you sure you want to remove worker ${workerId}`)) {
      this.props.apiClient.removeWorker(workerId)
        .then(() => {
          this.setState({
            ...this.state,
            "workers": this.state.workers.filter(worker => worker["worker_id"] !== workerId),
          });
        })
        .catch(error => {
          this.setState({ error })
        });
    }
  }

  onUpdateIntervalSeconds = (workerId, intervalSeconds) => {
    this.props.apiClient.updateWorkerIntervalSeconds(workerId, intervalSeconds)
      .catch(error => {
        this.setState({ error })
      });
  }

  onUpdateErrorResiliency = (workerId, errorResiliency) => {
    this.props.apiClient.updateWorkerErrorResiliency(workerId, errorResiliency)
      .catch(error => {
        this.setState({ error })
      });
  }

  onUpdateExecutor = (workerId, executor) => {
    this.props.apiClient.updateWorkerExecutor(workerId, executor)
      .catch(error => {
        this.setState({ error })
      });
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
    if (this.state.workers.length === 0) {
      return (
        <Grid container justify="center">
          <Typography variant='body1'>
            No workers
          </Typography>
        </Grid>
      )
    }
    const nowSeconds = Math.floor(Date.now() / 1000)
    return (
      <div>
        <Button variant="contained" color="primary">
          Create new worker
        </Button>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Interval (seconds)</TableCell>
                <TableCell>Error Resiliency (non-positive is none)</TableCell>
                <TableCell>Executor</TableCell>
                <TableCell>Executed minutes ago</TableCell>
                <TableCell>Operations</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {
                this.state.workers.map(worker => {
                  const {
                    "worker_id": workerId,
                    "module_name": moduleName,
                    args,
                    "interval_seconds": intervalSeconds,
                    "error_resiliency": errorResiliency,
                    "executor_slug": executor,
                    "last_executed_seconds": lastExecutedSeconds
                  } = worker;
                  return (
                    <TableRow key={workerId}>
                      <TableCell>
                        <Link to={`/worker/${workerId}`}>{workerId}</Link>
                      </TableCell>
                      <TableCell>
                        <Input type="number" value={intervalSeconds} onChange={e => {
                          e.preventDefault();
                          this.setState({
                            "workers": this.state.workers.map(worker => {
                              if (worker["worker_id"] !== workerId) {
                                return worker
                              }
                              return {
                                ...worker,
                                "interval_seconds": parseInt(e.target.value)
                              }
                            })
                          })
                        }}/>
                        <IconButton onClick={e => {
                          e.preventDefault()
                          this.onUpdateIntervalSeconds(workerId, intervalSeconds)}
                        }>
                          <CheckCircleIcon />
                        </IconButton>
                      </TableCell>
                      <TableCell>
                        <Input type="number" value={errorResiliency} onChange={e => {
                          e.preventDefault();
                          this.setState({
                            "workers": this.state.workers.map(worker => {
                              if (worker["worker_id"] !== workerId) {
                                return worker
                              }
                              return {
                                ...worker,
                                "error_resiliency": parseInt(e.target.value)
                              }
                            })
                          })
                        }}/>
                        <IconButton onClick={e => {
                          e.preventDefault()
                          this.onUpdateErrorResiliency(workerId, errorResiliency)}
                        }>
                          <CheckCircleIcon />
                        </IconButton>
                      </TableCell>
                      <TableCell>
                        <Select value={executor} onChange={e => {
                          e.preventDefault();
                          this.setState({
                            "workers": this.state.workers.map(worker => {
                              if (worker["worker_id"] !== workerId) {
                                return worker
                              }
                              return {
                                ...worker,
                                "executor_slug": e.target.value
                              }
                            })
                          })
                        }}>
                          {this.state.executors.map((executor, i) =>
                            <MenuItem key={i} value={executor}>{executor}</MenuItem>
                          )}
                        </Select>
                        <IconButton onClick={e => {
                          e.preventDefault()
                          this.onUpdateExecutor(workerId, executor)}
                        }>
                          <CheckCircleIcon />
                        </IconButton>
                      </TableCell>
                      <TableCell>{lastExecutedSeconds !== -1 ? Math.floor((nowSeconds - lastExecutedSeconds) / 60) : 'N/A'}</TableCell>
                      <TableCell>
                        <IconButton onClick={e => {
                          e.preventDefault();
                          this.onReplicate(moduleName, args, intervalSeconds)
                        }}>
                          <FileCopyIcon />
                        </IconButton>
                        <IconButton onClick={e => {
                          e.preventDefault();
                          this.onRemove(workerId)
                        }}>
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  )
                })
              }
            </TableBody>
          </Table>
        </TableContainer>
      </div>
    )
  }
}
