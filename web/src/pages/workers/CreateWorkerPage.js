import React, { Component } from 'react';
import { withRouter } from "react-router-dom";
import qs from "query-string";
import JsonEditorModal from "../../components/JsonEditorModal"
import { parseJsonOrObject } from "../../utils/jsonParsing"

class CreateWorkerPage extends Component {
  constructor(props) {
    super(props);
    const query = qs.parse(this.props.location.search);
    this.state = {
      "moduleName": query["module_name"] || "",
      "args": parseJsonOrObject(query["args"]),
      "intervalSeconds": parseInt(query["interval_seconds"]) || 60,
      "modalIsOpen": false
    };

    this.onSubmit = this.onSubmit.bind(this)
  }

  onSubmit(e) {
    this.submit();
    e.preventDefault()
  }

  submit() {
    const {moduleName, args, intervalSeconds} = this.state;
    this.props.apiClient.addWorker(moduleName, args, intervalSeconds)
      .then(() => {
        this.props.redirectTo("/workers/view");
      })
      .catch(error => {
        console.error(error.response.data);
        this.props.showErrorMessage(JSON.stringify(error.response.data))
      });
  }

  render() {
    return (
      <div>
        <b>Create new worker</b>
        <div>
          Module name:<br/>
          <input
            type="text"
            size={63}
            value={this.state.moduleName}
            onChange={e => {this.setState({"moduleName": e.target.value})}}
          /><br/>
          Args:<br/>
          <button onClick={() => {
            this.setState({"modalIsOpen": true})
          }}>Open JSON editor</button>
          <div>{JSON.stringify(this.state.args)}</div>
          Interval seconds:<br/>
          <input
            type="number"
            value={this.state.intervalSeconds}
            onChange={e => {this.setState({"intervalSeconds": parseInt(e.target.value)})}}
          /><br/>
          <button onClick={this.onSubmit}>Submit</button>
        </div>
        <JsonEditorModal
          value={this.state.args}
          onValueChange={newValue => this.setState({"args": newValue})}
          onClose={() => {this.setState({"modalIsOpen": false})}}
          isOpen={this.state.modalIsOpen}
        />
      </div>
    )
  }
}

export default withRouter(CreateWorkerPage)
