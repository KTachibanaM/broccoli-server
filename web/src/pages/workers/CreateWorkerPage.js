import React, { Component } from 'react';
import { withRouter } from "react-router-dom";
import qs from "query-string";

class CreateWorkerPage extends Component {
  constructor(props) {
    super(props);
    const query = qs.parse(this.props.location.search);
    this.state = {
      "module": query["module"] || "",
      "className": query["class_name"] || "",
      "argsStr": query["args"] || "{}",
      "intervalSeconds": parseInt(query["interval_seconds"]) || 60
    };

    this.onSubmit = this.onSubmit.bind(this)
  }

  onSubmit(e) {
    this.submit();
    e.preventDefault()
  }

  submit() {
    const {module, className, argsStr, intervalSeconds} = this.state;
    let args;
    try {
      args = JSON.parse(argsStr)
    } catch (e) {
      this.props.showErrorMessage("Arg is not valid JSON");
      return
    }
    this.props.schedulerClient.addWorker(module, className, args, intervalSeconds)
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
          Module:<br/>
          <input
            type="text"
            value={this.state.module}
            onChange={e => {this.setState({"module": e.target.value})}}
          /><br/>
          Class name:<br/>
          <input
            type="text"
            value={this.state.className}
            onChange={e => {this.setState({"className": e.target.value})}}
          /><br/>
          Args:<br/>
          <textarea
            cols="30" rows="5" style={{"resize": "none"}}
            value={this.state.argsStr}
            onChange={e => {this.setState({"argsStr": e.target.value})}}
          /><br/>
          Interval seconds:<br/>
          <input
            type="number"
            value={this.state.intervalSeconds}
            onChange={e => {this.setState({"intervalSeconds": parseInt(e.target.value)})}}
          /><br/>
          <button onClick={this.onSubmit}>Submit</button>
        </div>
      </div>
    )
  }
}

export default withRouter(CreateWorkerPage)
