import React from "react"
import ApiClient from "../../api/ApiClient";
import {
  Button,
  FormControl,
  FormGroup, Input, InputLabel, MenuItem, Select
} from "@material-ui/core";

interface Props {
  apiClient: ApiClient
}

interface State {
  loading: boolean,
  modules: string[],
  module: string,
  argsString: string,
  error?: Error
}

class JobsPage extends React.Component<Props, State> {
  constructor(props) {
    super(props);
    this.state = {
      loading: true,
      modules: [],
      module: "",
      argsString: "{}"
    }
  }

  componentDidMount() {
    this.props.apiClient.getOneOffJobModules()
      .then(modules => {
        this.setState({ modules })
      })
      .catch(error => [
        this.setState({ error })
      ])
      .finally(() => {
        this.setState({ loading: false })
      })
  }

  onRunJob = () => {

  }

  render() {
    let canParseArgs = true
    try {
      JSON.parse(this.state.argsString)
    } catch {
      canParseArgs = false
    }
    return (
      <FormGroup>
        <FormControl>
          <InputLabel>Module</InputLabel>
          <Select>
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
    )
  }
}

export default JobsPage
