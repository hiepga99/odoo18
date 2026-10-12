/** @odoo-module **/

import { browser } from "@web/core/browser/browser";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, onMounted, onWillUnmount } from "@odoo/owl";

const POLL_INTERVAL_MS = 2000;
const ACTIVE_STATUSES = new Set(["pending", "processing", "delete_pending"]);

export class RagProcessingProgress extends Component {
    static template = "ai_rag_document.RagProcessingProgress";
    static props = {
        ...standardFieldProps,
        statusField: { type: String },
        stageField: { type: String },
    };

    setup() {
        this.timer = null;
        this.refreshing = false;
        onMounted(() => this.scheduleRefresh(600));
        onWillUnmount(() => this.clearTimer());
    }

    get progress() {
        const value = Number(this.props.record.data[this.props.name] || 0);
        return Math.max(0, Math.min(value, 100));
    }

    get status() {
        return this.props.record.data[this.props.statusField];
    }

    get stage() {
        return this.props.record.data[this.props.stageField] || "Đang chờ cập nhật";
    }

    get barClass() {
        if (this.status === "error") {
            return "bg-danger";
        }
        if (this.status === "indexed") {
            return "bg-success";
        }
        return "progress-bar-striped progress-bar-animated bg-primary";
    }

    get shouldPoll() {
        return Boolean(this.props.record.resId) && ACTIVE_STATUSES.has(this.status);
    }

    clearTimer() {
        if (this.timer) {
            browser.clearTimeout(this.timer);
            this.timer = null;
        }
    }

    scheduleRefresh(delay = POLL_INTERVAL_MS) {
        this.clearTimer();
        if (this.shouldPoll) {
            this.timer = browser.setTimeout(() => this.refreshRecord(), delay);
        }
    }

    async refreshRecord() {
        if (this.refreshing || !this.shouldPoll) {
            return;
        }
        this.refreshing = true;
        try {
            if (!this.props.record.dirty && !document.hidden) {
                await this.props.record.load();
                this.props.record.model.notify();
            }
        } catch (error) {
            // A temporary network error must not break the form; retry next cycle.
            console.debug("RAG progress refresh failed", error);
        } finally {
            this.refreshing = false;
            this.scheduleRefresh();
        }
    }
}

export const ragProcessingProgress = {
    component: RagProcessingProgress,
    supportedTypes: ["integer"],
    extractProps: ({ options }) => ({
        statusField: options.status_field || "rag_status",
        stageField: options.stage_field || "rag_progress_stage",
    }),
};

registry.category("fields").add("rag_processing_progress", ragProcessingProgress);
