import React  from "react"
import { withRouter, RouteComponentProps } from "react-router-dom";
import {Button, FormControl, FormGroup, Input, InputLabel, Typography} from "@material-ui/core";

type Props = RouteComponentProps

interface State {
  loading: boolean
  error?: Error
  metadataStr: string
}

class Worker extends React.Component<Props, State> {
  private readonly workerId: string;

  constructor(props) {
    super(props);
    this.workerId = this.props.match.params.workerId as string;
    this.state = {
      "loading": true,
      "metadataStr": "[]"
    }
  }

  componentDidMount() {
    this.props.apiClient.getWorkerMetadata(this.workerId)
      .then(metadata => {
        this.setState({
          "metadataStr": JSON.stringify(metadata)
        })
      })
      .catch(error => {
        this.setState({ error })
      })
      .finally(() => {
        this.setState({
          "loading": false
        })
      })
  }

  render() {
    let canParseMetadata = true
    try {
      JSON.parse(this.state.metadataStr)
    } catch {
      canParseMetadata = false
    }
    return (
      <div>
        <Typography>{`Worker ${this.workerId}`}</Typography>
        <FormGroup>
          <FormControl margin='dense'>
            <InputLabel>Metadata</InputLabel>
            <Input
              multiline
              rows={5}
              rowsMax={5}
              value={this.state.metadataStr}
              onChange={e => {
                e.preventDefault()
                this.setState({"metadataStr": e.target.value})}
              }
              error={!canParseMetadata}
            />
          </FormControl>
          <FormControl margin='dense'>
            <Button
              variant="contained"
              color="secondary"
              onClick={e => {
                e.preventDefault()
                this.props.apiClient.setWorkerMetadata(this.workerId, JSON.parse(this.state.metadataStr))
              }}
              disabled={!canParseMetadata}
            >Submit</Button>
          </FormControl>
        </FormGroup>
      </div>
    )
  }
}

export default withRouter(Worker)
