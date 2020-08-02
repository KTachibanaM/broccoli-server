import React  from 'react';
import { withRouter, RouteComponentProps } from "react-router-dom";
import qs from "query-string";
import ApiClient from "../../api/ApiClient";
import {
  Button,
  CircularProgress,
  FormControl,
  FormGroup,
  Grid, Input, InputLabel,
  MenuItem,
  Select,
  Typography
} from "@material-ui/core";

type Props = {
  apiClient: ApiClient
} & RouteComponentProps

interface State {
  loading: boolean,
  modules: string[],
  error?: Error,
  moduleName: string,
  argsString: string,
  intervalSeconds: number,
}

class CreateWorkerPage extends React.Component<Props, State> {
  constructor(props) {
    super(props);
    const query = qs.parse(this.props.location.search);
    this.state = {
      "loading": true,
      "modules": [],
      "moduleName": query["module_name"] || "",
      "argsString": query["args"] || "{}",
      "intervalSeconds": parseInt(query["interval_seconds"]) || 60,
    };
  }

  componentDidMount() {
    this.props.apiClient.getWorkerModules()
      .then(modules => {
        this.setState({ modules })
      })
      .catch(error => {
        this.setState({ error })
      })
      .finally(() => {
        this.setState({ loading: false })
      })
  }

  onSubmit = () => {
    const {moduleName, argsString, intervalSeconds} = this.state;
    const args = JSON.parse(argsString)
    this.props.apiClient.addWorker(moduleName, args, intervalSeconds)
      .then(() => {
        this.props.history.push("/workers/view");
      })
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
    let canParseArgs = true
    try {
      JSON.parse(this.state.argsString)
    } catch {
      canParseArgs = false
    }
    return (
      <React.Fragment>
        <FormGroup>
          <FormControl>
            <InputLabel>Module</InputLabel>
            <Select
              value={this.state.moduleName}
              onChange={e => {
                e.preventDefault()
                this.setState({"moduleName": e.target.value as string})}
              }
            >
              {this.state.modules.map((module, i) => {
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
              rows={6}
              rowsMax={6}
              error={!canParseArgs}
            />
          </FormControl>
          <FormControl>
            <InputLabel>Interval seconds</InputLabel>
            <Input
              type="number"
              value={this.state.intervalSeconds}
              onChange={e => {
                e.preventDefault()
                this.setState({"intervalSeconds": parseInt(e.target.value)})
              }}
            />
          </FormControl>
          <FormControl>
            <Button
              variant="contained"
              color="secondary"
              onClick={e => {
                e.preventDefault();
                this.onSubmit()
              }}
              disabled={!canParseArgs}
            >Submit</Button>
          </FormControl>
        </FormGroup>
      </React.Fragment>
    )
  }
}

export default withRouter(CreateWorkerPage)
