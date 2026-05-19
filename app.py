from flask import Flask, jsonify, request, render_template, redirect, abort
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///portfolio.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    tech = db.Column(db.String(100), nullable=False)
    github_url = db.Column(
        db.String(250), nullable=True
    )  # Nullable=True means it's optional

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "tech": self.tech,
            "github_url": self.github_url,  # Include in API responses
        }


with app.app_context():
    db.create_all()


# --- HTML Frontend Routes ---


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/projects")
def get_projects_html():
    projects = db.session.scalars(db.select(Project)).all()
    return render_template("projects.html", projects=projects)


@app.route("/add", methods=["GET", "POST"])
def add_project_form():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        tech = request.form.get("tech")
        github_url = request.form.get("github_url")  #

        if not name or not description or not tech:
            return "Missing required fields", 400

        new_project = Project(
            name=name, description=description, tech=tech, github_url=github_url
        )
        db.session.add(new_project)
        db.session.commit()
        return redirect("/projects")

    return render_template("add_project.html")


# --- JSON API Routes ---


@app.route("/api/projects", methods=["GET"])
def get_projects_json():
    projects = db.session.scalars(db.select(Project)).all()
    return jsonify([project.to_dict() for project in projects])


@app.route("/api/projects", methods=["POST"])
def add_project_api():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json()

    required_fields = ["name", "description", "tech"]
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400

    new_project = Project(
        name=data["name"],
        description=data["description"],
        tech=data["tech"],
        github_url=data.get("github_url"),
    )
    db.session.add(new_project)
    db.session.commit()
    return jsonify(new_project.to_dict()), 201


@app.route("/api/projects/<int:project_id>", methods=["DELETE"])
def delete_project(project_id):
    project = db.session.get(Project, project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    db.session.delete(project)
    db.session.commit()
    return jsonify({"message": f"Project {project_id} successfully deleted"})


if __name__ == "__main__":
    app.run(debug=True)
